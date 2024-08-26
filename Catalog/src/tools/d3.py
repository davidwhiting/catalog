#################################################################
#################  D3 RENDERING FUNCTIONS  ######################
#################################################################

import pandas as pd
import numpy as np
import json
#import templates

## Note: Escape curly brackets {} with {{}} so that substitution within Python works properly
html_minimal_template = '''
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

    html_template = html_minimal_template.format(
        javascript=javascript_draw_only,
        headers=headers_json, 
        data=df_json)
    
    return html_template

def prepare_d3_data(df, start_term='SPRING 2024'):
    '''
    Prepare data for input into D3 figure
    '''
    # Constants
    BOX_WIDTH = 110
    BOX_HEIGHT = 40
    Y_GAP = 4
    BOX_SPACE = BOX_HEIGHT + Y_GAP
    SESSION_OFFSET = 60
    HEADER_ROW = 20

    def _set_colors(row):
        color_map = {
            'general': ('#3b8132', 'white'),
            'major': ('#135f96', 'white'),
            'required': ('#a30606', 'white'),
            'elective': ('#fdbf38', 'black')
        }
        return pd.Series(color_map.get(row['type'], ('white', 'black')))

    def _generate_semester_data(start_term, data_years=5):
        seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
        start_season, start_year = start_term.split()
        start_year = int(start_year)
        start_index = seasons.index(start_season)
        
        semester_data = []
        for year in range(start_year, start_year + data_years):  # Assuming 5 years of data
            for season in seasons[start_index:] + seasons[:start_index]:
                semester_data.append(f'{season} {year}')
        
        return pd.DataFrame({'course': semester_data})

    # Generate semester data
    headers = _generate_semester_data(start_term)
    headers['term'] = range(1, len(headers) + 1)
    headers['x'] = 10 + (headers.index * (2.25 * BOX_WIDTH + 20))
    headers['y'] = HEADER_ROW
    headers['color'] = 'lightgray'
    headers['textcolor'] = 'black'

    # Prepare course data
    df['x'] = 10 + ((df['term'] - 1) * (2.25 * BOX_WIDTH + 20)) + ((df['session'] - 1) * SESSION_OFFSET)
    df['y'] = HEADER_ROW + BOX_HEIGHT + ((df.groupby('term').cumcount()) * BOX_SPACE)
    df[['color', 'textcolor']] = df.apply(_set_colors, axis=1)
    df['course'] = df['course'] + f' ({df["credits"]})'

    # Combine headers and course data
    combined_data = pd.concat([headers, df], sort=False)
    combined_data['description'] = combined_data.get('prerequisites', '')

    # Select and order final columns
    final_columns = ['x', 'y', 'course', 'color', 'textcolor', 'term', 'credits', 'description']
    result = combined_data[final_columns].to_dict('records')

    return result