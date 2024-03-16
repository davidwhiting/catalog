import sys
import traceback
from h2o_wave import Q, ui, graphics as g
import templates

import pandas as pd
import numpy as np



def get_form_items(value):
    return [
        ui.text(f'spinbox_trigger={value}'),
        ui.spinbox(name='spinbox_trigger', label='Credits', trigger=True),
    ]

def single_query(query, cursor):
    # convenience function for sqlite3 db queries that return one value
    cursor.execute(query)
    q_result = cursor.fetchone()
    if q_result is not None:
        result = q_result[0]
    else:
        result = None

    return result

## For some reason, this function works in the app.py file but not in the included utils.py file.
## Need to figure out why this is.

#def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
#    if not q.client.cards:
#        return
#    for name in q.client.cards.copy():
#        if name not in ignore:
#            del q.page[name]
#            q.client.cards.remove(name)

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

def prepare_d3_data(df, start_term='SPRING 2024'):

    def set_colors(row):
        if row['type'] == 'general':
            return pd.Series(['green', 'white'])
        elif row['type'] == 'major':
            return pd.Series(['blue', 'white'])
        elif row['type'] == 'required':
            return pd.Series(['red', 'white'])
        elif row['type'] == 'elective':
            return pd.Series(['yellow', 'black'])
        else:
            return pd.Series(['white', 'black'])  # default colors

    def generate_header_data(start_semester, num_periods, data_df = df):
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
        df['width'] = df['term'].apply(lambda x: 190 if 'SUMMER' in x else 260)
        df['offset'] = df['term'].apply(lambda x: 2 if 'SUMMER' in x else 3)
        df['fontsize'] = '14px'
        df['description'] = ''
        df['space'] = 40
        df['xpos'] = df['width'] + df['space']

        x0 = 10
        # Calculate the cumulative sum of 'xpos'
        df['x'] = df['xpos'].cumsum()
        df['x'] = df['x'].shift(1)
        df.loc[0, 'x'] = 0
        df['x'] = df['x'] + x0
        df['y'] = 10
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

        return df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 
                   'fontsize', 'period', 'name', 'credits', 'description']]

    # Prepare data for the D3 figure

    max_period = max(df['period'])
    headers = generate_header_data(start_term, max_period)

    df['description'] = df['prerequisite']
    df['width'] = 120
    # Calculate 'x' column
    df = pd.merge(df, headers[['period','x']], on='period', how='left')
    df['x'] += 70*(df['session']-1)

    # Calculate 'y' column
    df = df.sort_values(by=['period', 'session', 'seq' ])
    df['y_row'] = df.groupby('period').cumcount() + 1
    df['y'] = 70 + 45 * (df['y_row'] - 1)

    # Create rectangle colors
    df[['color', 'textcolor']] = df.apply(set_colors, axis=1)

    # Set text offset multiplier to 1 and text fontsize
    df['offset'] = 1
    df['fontsize'] = '12px'
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'
    
    df = df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 'fontsize', 'period', 'session', 'type', 'name', 'credits', 'description']]

    return df, headers