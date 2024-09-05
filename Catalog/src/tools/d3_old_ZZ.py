#################################################################
#################  D3 RENDERING FUNCTIONS  ######################
#################################################################
import json
import pandas as pd
import numpy as np

import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code_minimal = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}   
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>
  <script src='https://d3js.org/d3.v5.js'></script>
</head>
<body>
  <script type="module">
    {javascript}
    render({headers});
    render({data});
  </script>
</body>
</html>
'''

# javascript_draw_only takes coordinates from python rather than computing itself in d3

javascript_draw_only = '''
    //const screenWidth = 1200;
    const screenWidth = 800;
    const boxHeight = 40;
    const textOffsetX = 20;
    const textOffsetY = 25;

    function drawRect(x, y, width, printname, color, textcolor, offset, fontsize, description) {
        var g = zoomable.append("g");
        g.append("rect")
            .attr("x", x)
            .attr("y", y)
            .attr("width", width)
            .attr("height", boxHeight)
            .style("fill", color)
            .classed("movable", true); 
        g.append("text")
            .attr("x", x + offset*textOffsetX)
            .attr("y", y + textOffsetY)
            .text(printname)
            .attr("fill", textcolor)
            .style("font-size", fontsize)
            .style("font-family", "Arial")
            .style("font-weight", "bold")
            .classed("movable", true); 
        // Add a tooltip
        g.append("description")
            .text(description);
    }
    function render(data) {
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            if (item.x === undefined || 
                item.y === undefined ||
                item.width === undefined || 
                item.printname === undefined || 
                item.color === undefined || 
                item.textcolor === undefined ||
                item.offset === undefined ||
                item.fontsize === undefined ||
                item.description === undefined) {
                    console.error('Error: Missing property in item ' + i);
                    continue;
            }
            drawRect(item.x, item.y, item.width, item.printname, item.color, 
                item.textcolor, item.offset, item.fontsize, item.description);
        }
    }

    // Select the body
    var body = d3.select("body");
    // Zoom behavior
    var svg = body.append('svg')
        .attr('id', 'datavizArea')
        .attr('height', 290)
        .attr('width', 690);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
        .on("zoom", function() {
            zoomable.attr("transform", d3.event.transform);
        });
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.75).translate(0, 0));
'''

def create_html_template_old(df, start_term):
    '''
    Function that takes the q.user.student_data['schedule'] dataframe 
    and converts it to the html_template to create the Javascript D3 figure
    '''
    ### accept start_term both as 'spring2024' and 'Spring 2024'. Make sure to
    ### return as the latter
    ##if ' ' in start_term:
    ##    start = start_term.upper()
    ##else:
    ##    season = start_term[:-4]
    ##    year = start_term[-4:]
    ##    start = f"{season.upper()} {year}"

    start_term = start_term.upper()
    if ' ' not in start_term:
        season, year = start_term[:-4], start_term[-4:]
        start_term = f"{season} {year}"

    # rename because the function uses 'period' rather than 'term'
    # to do: inefficient, need to rewrite
    df_input = df.copy()
    df_input.rename(columns={'term': 'period'}, inplace=True)

    df_display, headers_display = prepare_d3_data(df_input, start_term)
    df_json = df_display.to_json(orient='records')
    headers_json = headers_display.to_json(orient='records')

    html_template = html_code_minimal.format(
        javascript=javascript_draw_only,
        headers=headers_json, 
        data=df_json)
    
    return html_template

def create_html_template(df, start_term):
    '''
    Function that takes the q.user.student_data['schedule'] dataframe 
    and converts it to the html_template to create the Javascript D3 figure
    '''
    ### accept start_term both as 'spring2024' and 'Spring 2024'. Make sure to
    ### return as the latter
    start_term = start_term.upper()
    if ' ' not in start_term:
        season, year = start_term[:-4], start_term[-4:]
        start_term = f"{season} {year}"

    df_display, headers_display = prepare_d3_data(df, start_term)
    df_json = df_display.to_json(orient='records')
    headers_json = headers_display.to_json(orient='records')

    html_template = html_code_minimal.format(
        javascript=javascript_draw_only,
        headers=headers_json, 
        data=df_json)
    
    return html_template

def generate_header_data(start_semester, num_periods, data_df):

    # Constants
    HEADER_WIDTH = 260
    SUMMER_HEADER_WIDTH = 190
    HEADER_OFFSET = 3
    SUMMER_HEADER_OFFSET = 2

    X_GAP = 40
    X_OFFSET = 10
    Y_GAP = 4
    Y_OFFSET = 10
    SESSION_OFFSET = 70
    HEADER_ROW = 20    

    seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
    semester_data = []
    start_season, start_year = start_semester.split(' ')
    start_year = int(start_year)
    season_index = seasons.index(start_season)
    year = start_year
    period = 0

    while period < num_periods:
        for j in range(season_index, len(seasons)):
            semester_data.append(f'{seasons[j]} {year}')
            period += 1

            # Break the loop when i equals num_periods
            if period == num_periods:
                break

        # Reset the season index to start from 'WINTER' for the next year
        season_index = 0
        year += 1

    df = pd.DataFrame(semester_data, columns=['term'])
    df['width'] = df['term'].apply(lambda x: SUMMER_HEADER_WIDTH if 'SUMMER' in x else HEADER_WIDTH)
    df['offset'] = df['term'].apply(lambda x: SUMMER_HEADER_OFFSET if 'SUMMER' in x else HEADER_OFFSET)
    df['fontsize'] = '14px'
    df['description'] = ''
    df['space'] = X_GAP
    df['xpos'] = df['width'] + df['space']

    x0 = 10
    # Calculate the cumulative sum of 'xpos'
    df['x'] = df['xpos'].cumsum()
    df['x'] = df['x'].shift(1)
    df.loc[0, 'x'] = 0
    df['x'] = df['x'] + X_OFFSET
    df['y'] = Y_OFFSET
    df['color'] = 'lightgray'
    df['textcolor'] = 'black'
    df['period'] = np.arange(1, num_periods+1)

    df.drop
    # Sum credits per period and convert to a DataFrame
    total_credits = data_df.groupby('period')['credits'].sum().sort_index()
    total_credits_df = total_credits.reset_index()

    df = pd.merge(df, total_credits_df, on='period', how='inner')
    df['name'] = df['term']
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'

    # quick fix for period needed here

    return df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 
               'fontsize', 'period', 'name', 'credits', 'description']]


def prepare_d3_data(df_input, start_term='SPRING 2024'):
    '''
    Prepare data for input into D3 figure
    Note: The D3 function uses 'period' rather than 'term'... we may need to update that 
    Note: Need to fix so the inefficient hack is not required
          current 'term' -> 'name' (check this)
          current 'period' -> 'term'
    '''

    # quick hack to fix the fact this uses 'period' instead of 'term': 
    df = df_input.copy()
    df.rename(columns={'term': 'period'}, inplace=True)

    # Constants
    BOX_WIDTH = 120
    BOX_HEIGHT = 40
    Y_GAP = 4
    Y_OFFSET = 45
    SESSION_OFFSET = 70
    BOX_SPACE = BOX_HEIGHT + Y_GAP
    HEADER_ROW = 20    

    def _set_colors(row):
        # Use UMGC Colors
        green = '#3b8132'
        blue = '#135f96'
        red = '#a30606'
        yellow = '#fdbf38'
        black = 'black' # alternatively replace 
        white = 'white'

        color_map = {
            'general': (green, white),
            'major': (blue, white),
            'required': (red, white),
            'elective': (yellow, black)
        }
        return pd.Series(color_map.get(row['type'], (white, black)))

   # Prepare data for the D3 figure

    max_period = max(df['period'])
    headers = generate_header_data(start_term, max_period, df)

    df['description'] = df['prerequisites']
    df['width'] = BOX_WIDTH
    # Calculate 'x' column
    df = pd.merge(df, headers[['period','x']], on='period', how='left')
    df['x'] += SESSION_OFFSET*(df['session']-1)

    # Calculate 'y' column
    df = df.sort_values(by=['period', 'session', 'seq' ])
    df['y_row'] = df.groupby('period').cumcount() + 1
    df['y'] = SESSION_OFFSET + Y_OFFSET * (df['y_row'] - 1)

    # Create rectangle colors
    df[['color', 'textcolor']] = df.apply(_set_colors, axis=1)

    # Set text offset multiplier to 1 and text fontsize
    df['offset'] = 1
    df['fontsize'] = '12px'
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'
    
    df = df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 'fontsize', 'period', 'session', 'type', 'course', 'credits', 'description']]

    return df, headers
