#################################################################
#################  D3 RENDERING FUNCTIONS  ######################
#################################################################

import pandas as pd
import numpy as np
import json
import templates

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
        
        return pd.DataFrame({'name': semester_data})

    # Generate semester data
    headers = _generate_semester_data(start_term)
    headers['period'] = range(1, len(headers) + 1)
    headers['x'] = 10 + (headers.index * (2.25 * BOX_WIDTH + 20))
    headers['y'] = HEADER_ROW
    headers['color'] = 'lightgray'
    headers['textcolor'] = 'black'

    # Prepare course data
    df['x'] = 10 + ((df['period'] - 1) * (2.25 * BOX_WIDTH + 20)) + ((df['session'] - 1) * SESSION_OFFSET)
    df['y'] = HEADER_ROW + BOX_HEIGHT + ((df.groupby('period').cumcount()) * BOX_SPACE)
    df[['color', 'textcolor']] = df.apply(_set_colors, axis=1)
    df['name'] = df['name'] + f' ({df["credits"]})'

    # Combine headers and course data
    combined_data = pd.concat([headers, df], sort=False)
    combined_data['description'] = combined_data.get('prerequisites', '')

    # Select and order final columns
    final_columns = ['x', 'y', 'name', 'color', 'textcolor', 'period', 'credits', 'description']
    result = combined_data[final_columns].to_dict('records')

    return result

def create_html_template(df, start_term):
    '''
    Function that takes the dataframe and converts it to the html_template to create the Javascript D3 figure
    '''
    start_term = start_term.upper()
    if ' ' not in start_term:
        season, year = start_term[:-4], start_term[-4:]
        start_term = f"{season} {year}"

    data = prepare_d3_data(df, start_term)
    data_json = json.dumps(data)

    html_template = templates.html_code_minimal.format(
        javascript=templates.javascript_draw_only,
        data=data_json)
    
    return html_template