import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates
import utils
import pandas as pd

from utils import add_card, single_query, query_row

def dialog_description(row: int) -> ui.Dialog:
    """
    Dialog for viewing course description.
    """

    #if row == 0:
    #    image_path = 'https://images.unsplash.com/photo-1587049016823-69ef9d68bd44'
    #elif row == 2:
    #    image_path = 'https://images.unsplash.com/photo-1552975084-6e027cd345c2'
    #else:
    #    image_path = 'https://images.unsplash.com/photo-1574276254982-d209f79d673a'

    dialog = ui.dialog(
        name='dialog_description',
        title='Course Description',
        items=[ui.image(title='Image', path=image_path, width='100%')],
        closable=True,
        events=['dismissed']
    )

    return dialog

async def render_project_table(data, location='middle_vertical', title='Project Status Table', height='520px'):

    project_table_columns = [
        ui.table_column(
            name='id',
            label='Id',
            sortable=True,
            min_width='40px'
        ),
        ui.table_column(
            name='rank',
            label='Rank',
            sortable=True,
            min_width='60px'
        ),
        ui.table_column(
            name='category',
            label='Category',
            sortable=True,
            filterable=True,
            searchable=True,
            min_width='120px'
        ),
        ui.table_column(
            name='description',
            label='Description',
            cell_type=ui.markdown_table_cell_type(),
            min_width='300px',
            searchable=True
        ),
        ui.table_column(
            name='status',
            label='Status',
            cell_type=ui.progress_table_cell_type(),
            sortable=True,
            min_width='100px'
        ),
        ui.table_column(
            name='tags',
            label='Tags',
            cell_type=ui.tag_table_cell_type(
                name='',
                tags=[
                    ui.tag(label='Database', color='$green'),
                    ui.tag(label='UI', color='$blue'),
                    ui.tag(label='Wave', color='$orange'),
                    ui.tag(label='Code', color='$purple'),
                    ui.tag(label='Data', color='$red')
                ]
            ),
            searchable=True
        ),
        ui.table_column(
            name='menu',
            label='Menu',
            cell_type=ui.menu_table_cell_type(
                commands=[
                    ui.command(name='view_transaction', label='View Transaction', icon='Shop'),
                    ui.command(name='view_image', label='View Image', icon='ImageSearch')
                ]
            ),
            min_width='60px'
        )
    ]
    project_table_rows = [
        ui.table_row(
            name=row['id'],
            cells=[
                row['id'],
                row['rank'],
                row['category'],
                row['description'],
                row['status'],
                row['tags']
            ]
        ) for row in data
    ]
    card = ui.form_card(
        box=location,
        items=[
            ui.text(title, size=ui.TextSize.XL),
            ui.table(
                name='transactions',
                columns=project_table_columns,
                rows=project_table_rows,
                # pagination=False,
                groupable=True,
                # resettable=True,
                # downloadable=True,
                events=['page_change'],
                height=height
            ),
        ]
    )
    return card

project_table_columns = [
    ui.table_column(
        name='id',
        label='Id',
        min_width='40px'
    ),
    ui.table_column(
        name='category',
        label='Category',
        sortable=True,
        filterable=True,
        searchable=True,
        min_width='120px'
    ),
    ui.table_column(
        name='description',
        label='Description',
        cell_type=ui.markdown_table_cell_type(),
        min_width='200px',
        searchable=True
    ),
    ui.table_column(
        name='status',
        label='Status',
        cell_type=ui.progress_table_cell_type(),
        sortable=True,
        min_width='100px'
    ),
    ui.table_column(
        name='tags',
        label='Tags',
        cell_type=ui.tag_table_cell_type(
            name='',
            tags=[
                ui.tag(label='Beverage', color='$green'),
                ui.tag(label='Home', color='$blue'),
                ui.tag(label='Code', color='$purple'),
                ui.tag(label='Data', color='$red')
            ]
        ),
        searchable=True
    ),
    ui.table_column(
        name='menu',
        label='Menu',
        cell_type=ui.menu_table_cell_type(
            commands=[
                ui.command(name='view_transaction', label='View Transaction', icon='Shop'),
                ui.command(name='view_image', label='View Image', icon='ImageSearch')
            ]
        ),
        min_width='60px'
    )
]

interview_questions = [
    'Have you ever attended a college or university before?',
    'Are you enrolling full-time or part-time?',
    '[If part-time]: Are you working full-time?',
    '[If part-time & working full-time]: Are you attending evening classes?',
    'Are you in-state, out-of-state, or military?'
]

def render_debug_card(q, location='d3'):
    content = f'''
### All parameters?
{q}

### App Parameters
{q.app}

### User Parameters
{q.user}

### Client Parameters
{q.client}
    '''
    return ui.markdown_card(box=location, title='Debugging Information', content=content )

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

def render_tag_column(width='120'):
    result = ui.table_column(
        name='tag', 
        label='Type', 
        max_width=width,
        filterable=True,
        cell_type=ui.tag_table_cell_type(
            name='tags',
            tags=[
                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                ui.tag(label='REQUIRED', color='$red'),
                ui.tag(label='GENERAL', color='#046A38'),
                ui.tag(label='MAJOR', color='#1565C0'),
            ]
        )
    )
    return result

def render_major_table_group(group_name, record_type, records, collapsed):
    return ui.table_group(group_name, [
        ui.table_row(
            name=str(record['id']),
            cells=[
                record['course'],
                record['title'],
                str(record['credits']),
                #record['description'],
                record['type'].upper(),
            ]
        ) for record in records if record['type'].upper() == record_type
    ], collapsed=collapsed)

async def render_major_table(q, records, location='bottom_vertical', width='100%', ge=False, elective=False):
    return add_card(q, 'my_test_table', ui.form_card(
        #        box=ui.box(location, width=table_width, height=table_height),
        box=ui.box(location, height='350px', width=width),
        items=[
            #ui.text(title, size=ui.TextSize.L),
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='350px',
                columns=[
                    # ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
                    ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300',
                                    cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                                    align='center'),
                    ui.table_column(
                        name='tag',
                        label='Type',
                        min_width='190',
                        filterable=True,
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='menu', label='Menu', max_width='150',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                    #                    # ui.command(name='delete', label='Delete'),
                        ])
                                )
                ],
                groups=[
                    render_major_table_group(
                        'Required Major Core Courses',
                        'MAJOR',
                        records,
                        True),
                    render_major_table_group(
                        'Required Related Courses/General Education',
                        'REQUIRED,GENERAL',
                        records,
                        True),
                    render_major_table_group(
                        'Required Related Courses/Electives',
                        'REQUIRED,ELECTIVE',
                        records,
                        True),
                    #render_major_table_group(
                    #    'General Education',
                    #    'GENERAL',
                    #    major_records,
                    #    True),
                    #render_major_table_group(
                    #    'Electives',
                    #    'ELECTIVE',
                    #    major_records,
                    #    True)
            # ui.text(title, size=ui.TextSize.L),

        ])]
    ))



def create_table_group(group_name, record_type, records, collapsed):
    return ui.table_group(group_name, [
        ui.table_row(
            name=str(record['seq']),
            cells=[
                record['name'], 
                record['title'], 
                str(record['credits']), 
                #record['description'],
                record['type'].upper(), 
            ]
        ) for record in records if record['type'].upper() == record_type
    ], collapsed=collapsed)

def render_course_table2(q, records,
                         which=['MAJOR','REQUIRED'],
                         title='',
                         location='middle_horizontal',
                         table_height='100%',
                         table_width='100%'):
    # Renders a table for the courses tab

    #table_name = 'table_' + '_'.join(which)
    table_name = 'table_render_course2'
    result = add_card(q, table_name, ui.form_card(
#        box=ui.box(location, width=table_width, height=table_height),
        box=ui.box(location),
        items=[
            #ui.text(title, size=ui.TextSize.L),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                #height='800px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='course', label='Course', searchable=True, min_width='100'),
                    ui.table_column(name='title', label='Title', searchable=True, min_width='180', max_width='300', cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', min_width='50', align ='center'),
                    #ui.table_column(name='description', label='Description', searchable=False, max_width='150',
                    #    cell_overflow='tooltip',
                    #    #cell_overflow='wrap',
                    #    #cell_type=ui.markdown_table_cell_type(target='_blank'),
                    #),
                    tag_column,
                    ui.table_column(name='menu', label='Menu', max_width='150',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                            #ui.command(name='delete', label='Delete'),
                        ])
                    )
                ],
                groups=[
                    create_table_group('Required Major Core Courses', 'MAJOR', records, False),
                    create_table_group('Required Related Courses', 'REQUIRED', records, True),
                    create_table_group('Selected General Education Courses', 'GENERAL', records, True),
                    create_table_group('Selected Elective Courses', 'ELECTIVE', records, True),
                ]
            )
        ]
    ))

    return result

def render_course_table(q, records, which=['MAJOR'], title='Major Required Courses', location='middle_horizontal', table_height='480px', table_width='700px'):
    # Renders a table for the courses tab

    table_name = 'table_' + '_'.join(which)

    result = add_card(q, table_name, ui.form_card(
        box=ui.box(location, width=table_width, height=table_height),
        items=[
            ui.text(title, size=ui.TextSize.XL),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='400px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='text', label='Course', searchable=False, max_width='100'),
                    ui.table_column(name='title', label='Title', searchable=False, max_width='180', cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', max_width='50'),
                    ui.table_column(
                        name='tag', 
                        label='Course Type', 
                        max_width='150',
                        filterable=True, 
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='description', label='Description', searchable=False, max_width='60',
                        cell_overflow='tooltip', 
                        #cell_overflow='wrap', 
                        #cell_type=ui.markdown_table_cell_type(target='_blank'),
                    ),

#                    ui.table_column(name='actions', label='Menu', max_width='150',
#                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
#                            ui.command(name='description', label='Course Description'),
#                            ui.command(name='prerequisites', label='Show Prerequisites'),
#                            #ui.command(name='delete', label='Delete'),
#                        ])
#                    )
                ],
                rows=[ui.table_row(
                    name=str(record['seq']),
                    cells=[
                        #str(record['seq']), 
                        record['name'], 
                        record['title'], 
                        str(record['credits']), 
                        record['type'].upper(), 
                        record['description'], 
                    ]
                ) for record in records if record['type'].upper() in which ]
            )
        ]
    ))

    return result

async def render_majors_discovery(q, program_id, compare=False):
    '''
    Create the bottom half of the majors page given a program_id
    Compare: need to fix
        For making side-by-side comparisons
    '''

    # make this query into a view: major_records_view

    query = '''
        SELECT 
            id,
            course, 
            course_type as type,
            title,
            credits,
            pre,
            pre_credits,
            substitutions,
            description
        FROM program_requirements_view
        WHERE program_id = ?
    '''
    df = pd.read_sql_query(query, q.app.conn, params=(program_id,))
    major_records = df.to_dict('records')

    #query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    #df = pd.read_sql_query(query, q.app.conn, params=(program_id,))
    #rows = df.to_dict('records')
    #row = rows[0]

    if compare:
        #width='50%'
        card_location = 'horizontal'
    else:
        #width='100%'
        card_location = 'vertical'

    await render_major_dashboard(q, program_id, location='middle_' + card_location)
    await render_major_table(q, major_records, 'bottom_' + card_location)

def render_ge_table(q, records, which=['GENERAL'], title='Select General Education Courses', location='middle_horizontal', table_height='500px', table_width='700px'):
    # Renders a table for the courses tab

    table_name = 'table_' + '_'.join(which)

    result = add_card(q, table_name, ui.form_card(
        box=ui.box(location, width=table_width, height=table_height),
        items=[
            ui.text(title, size=ui.TextSize.XL),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='400px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='text', label='Course', searchable=False),
                    ui.table_column(name='credits', label='Credits', data_type='number'),
                    ui.table_column(
                        name='tag', 
                        label='Course Type', 
                        filterable=True, 
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='actions', label='Menu',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='view_description', label='Course Description'),
                            ui.command(name='view_prerequisites', label='Show Prerequisites'),
                            #ui.command(name='delete', label='Delete'),
                        ])
                    )
                ],
                rows=[ui.table_row(
                    name=str(record['seq']),
                    cells=[
                        #str(record['seq']), 
                        record['name'], 
                        str(record['credits']), 
                        record['type'].upper(), 
                    ]
                ) for record in records if record['type'].upper() in which ]
            )
        ]
    ))

    return result

def render_elective_table(q, records, which=['ELECTIVE'], title='Select Elective Courses', location='middle_horizontal', table_height='500px', table_width='700px'):
    # Renders a table for the courses tab

    table_name = 'table_' + '_'.join(which)

    result = add_card(q, table_name, ui.form_card(
        box=ui.box(location, width=table_width, height=table_height),
        items=[
            ui.text(title, size=ui.TextSize.XL),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='400px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='text', label='Course', searchable=False),
                    ui.table_column(name='credits', label='Credits', data_type='number'),
                    ui.table_column(
                        name='tag', 
                        label='Course Type', 
                        filterable=True, 
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='actions', label='Menu',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='view_description', label='Course Description'),
                            ui.command(name='view_prerequisites', label='Show Prerequisites'),
                            #ui.command(name='delete', label='Delete'),
                        ])
                    )
                ],
                rows=[ui.table_row(
                    name=str(record['seq']),
                    cells=[
                        #str(record['seq']), 
                        record['name'], 
                        str(record['credits']), 
                        record['type'].upper(), 
                    ]
                ) for record in records if record['type'].upper() in which ]
            )
        ]
    ))

    return result

def select_semester(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='start_term', 
                label='Start Term', 
                value=q.args.start_term,
                trigger=True,
                width=menu_width,
                choices=[
                    ui.choice(label="Spring 2024"),
                    ui.choice(label="Summer 2024"),
                    ui.choice(label="Fall 2024"),
                    ui.choice(label="Winter 2025"),
                ]
            ),
        ]
    )

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
old_meta = ui.meta_card(
        box='', 
        title='UMGC Wave App',
        theme='ember',
        layouts=[
            ui.layout(
                breakpoint='xs', 
                min_height='100vh', 
                zones=[
                    ui.zone('header'),
                    ui.zone('content', zones=[
                        # Specify various zones and use the one that is currently needed. 
                        # Empty zones are ignored.
                        ui.zone('top', zones=[
                            ui.zone('top_vertical'),
                            ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('dashboard', direction=ui.ZoneDirection.ROW),
                        ]),
                        ui.zone('middle', zones=[
                            ui.zone('middle_vertical'),
                            #ui.zone('middle_vertical2'), # for compare, figure out how to fix this
                            ui.zone('middle_horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('middle_horizontal2', direction=ui.ZoneDirection.ROW, wrap='stretch'),
                            ui.zone('d3', direction=ui.ZoneDirection.ROW),
                        ]),
                        ui.zone('bottom', zones=[
                            ui.zone('bottom_vertical'),
                            #ui.zone('bottom_vertical2'),
                            ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('vertical'),
                            ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                        ]),
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )

toggle = ui.form_card(box='rightgrid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

transfer_toggle = ui.form_card(box='grid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])



markdown = ui.form_card(
    box='leftnote',
    items=[ui.text(templates.sample_markdown)]
)

############################################################
#
# Try converting a dataframe directly into a wave table
#
############################################################

@app('/demo')
async def serve(q: ui.Request):
    if q.client.initial:
        q.page['meta'] = ui.meta_card(box='')
        q.page['controls'] = ui.form_card(box='1 1 2 2', items=[
            ui.textbox(name='row', label='Row'),
            ui.textbox(name='column', label='Column'),
            ui.textbox(name='value', label='Value'),
            ui.button(name='update', label='Update', primary=True),
        ])
        q.page['table'] = ui.table_card(
            box='1 3 5 5', 
            title='Data', 
            rows=to_rows(df), 
            columns=to_columns(df)
        )
        await q.page.save()
    elif q.args.update:
        row = int(q.args.row)
        column = q.args.column
        value = q.args.value
        df.at[row, column] = value # update dataframe
        q.page['table'].rows = to_rows(df)
        await q.page.save()

def to_rows(df):
    return [ui.table_row(name=str(i), cells=[str(x) for x in row]) for i, row in df.iterrows()]

def to_columns(df):
    return [ui.table_column(name=col, label=col, sortable=True, editable=False) for col in df.columns]

############### Example using pandas dataframes

import pandas as pd
from h2o_wave import Q, main, app, ui

# Sample DataFrame
data = {
    'id': [1, 2, 3],
    'name': ['John', 'Alice', 'Bob'],
    'title': ['Engineer', 'Manager', 'Designer'],
    'description': ['John is a skilled engineer.', 'Alice oversees project management.', 'Bob specializes in UI/UX design.']
}
df = pd.DataFrame(data)

@app('/table_with_description')
async def serve(q: Q):
    # Define column definitions
    columns = [
        ui.table_column(name='id', label='ID', link=True),
        ui.table_column(name='name', label='Name'),
        ui.table_column(name='title', label='Title')
    ]

    # Create rows from the DataFrame
    rows = [ui.table_row(**{col.name: row[col.name] for col in columns}) for _, row in df.iterrows()]

    # Create the table
    table = ui.table(
        name='example_table',
        columns=columns,
        rows=rows,
        downloadable=True
    )

    # Respond to clicks on the ID column
    if q.client.initialized:
        selected_id = q.client.selected_id
        if selected_id is not None:
            # Find the corresponding description
            description = df.loc[df['id'] == selected_id, 'description'].iloc[0]
            q.page['description'] = ui.text(description)

    # Create the UI
    q.page['example'] = ui.form_card(
        box='1 1 4 6',
        items=[table]
    )

    await q.page.save()

@main('/table_with_description')
async def main(q: Q):
    if q.args.row_clicked:
        q.client.selected_id = q.args.row_clicked['id']
    await serve(q)
