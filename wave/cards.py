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

async def render_home_cards(q, width='25%'):
    add_card(q, 'student_guest', ui.wide_info_card(
        box=ui.box('top_horizontal', width=width),
        name='',
        icon='Contact',
        title='Guests',
        caption='Login not required to use this app.'
    ))
    add_card(q, 'login',
        ui.wide_info_card(
            box=ui.box('top_horizontal', width=width),
            name='login',
            title='Login',
            caption='User roles: *admin*, *coach*, *student*, *prospect*.',
            icon='Signin')
    )
    add_card(q, 'import',
        ui.wide_info_card(
            box=ui.box('top_horizontal', width=width),
            name='import',
            title='Import',
            caption='Future state: Import UMGC student info.',
            icon='Import')
    )
    add_card(q, 'personalize',
        ui.wide_info_card(
            box=ui.box('top_horizontal', width=width),
            name='person',
            title='Personalize',
            caption='User adds new info or confirms imported info.',
            icon='UserFollowed')
    )

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

major_recommendation_card = ui.form_card(
    box=ui.box('top_horizontal', width='350px'),
    # box=ui.box('d3', width='300px'), # min width 200px
    items=[
        ui.choice_group(
            name='recommendation_group',
            label='Recommend a major based on ...',
            choices=[
                ui.choice('A', label='My interests'),
                ui.choice('B', label='My skills'),
                ui.choice('C', label='Students like me'),
                ui.choice('D', label='The shortest time to graduate'),
            ]),
        #                ui.slider(name='slider', label='Max Credits per Term', min=1, max=15, step=1, value=9),
        ui.inline(
            items=[
                ui.button(name='show_recommendations', label='Submit', primary=True),
                ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
            ]
        )
    ]
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

tag_column = ui.table_column(
    name='tag', 
    label='Type', 
    min_width='100',
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

async def render_major_dashboard(q, program_id, location, width='100%'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param program_id: id of program to be displayed
    :param location: page location to display
    '''

    # get program name
    query = '''
        SELECT b.name || ' in ' || a.name as degree_program
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = query_row(query, (program_id,), q.app.c)
    title = row[0]

    # get program summary
    query = '''
        SELECT major, related_ge, related_elective, remaining_ge, remaining_elective, total
        FROM program_requirements
        WHERE program_id = ?
    '''
    row = query_row(query, (program_id,), q.app.c)
    major, related_ge, related_elective, remaining_ge, remaining_elective, total = row

    return add_card(q, 'major_dashboard', ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.text(title + ': Credits', size=ui.TextSize.L),
            ui.stats(
                # justify='between',
                items=[
                    ui.stat(
                        label='Major',
                        value=str(major),
                        caption='Required Core',
                        icon='Trackers'),
                    ui.stat(
                        label='Required',
                        value=str(related_ge + related_elective),
                        caption='Required Related',
                        icon='News'),
                    ui.stat(
                        label='General Education',
                        value=str(remaining_ge),
                        caption='Remaining GE',
                        icon='TestBeaker'),
                    ui.stat(
                        label='Elective',
                        value=str(remaining_elective),
                        caption='Remaining Elective',
                        icon='Media'),
                    ui.stat(
                        label='TOTAL',
                        value=str(total),
                        caption='Total Credits',
                        icon='Education'),
            ])
    ]))

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

#async def render_majors_discovery_old(q, program_id, compare=False):
#    '''
#    Create the bottom half of the majors page given a program_id
#    Compare: need to fix
#        For making side-by-side comparisons
#    '''
#    query = '''
#        SELECT b.name || ' in ' || a.name as degree_program
#        FROM programs a, degrees b
#        WHERE a.id = ? AND a.degree_id = b.id
#    '''
#    row = query_row(query, (program_id,), q.app.c)
#    title = row[0]
#
#    # make this query into a view: major_records_view
#
#    query = '''
#        SELECT
#            id,
#            course,
#            type,
#            course_type_id,
#            title,
#            credits,
#            description,
#            pre,
#            pre_credits,
#            substitutions
#        FROM major_dashboard_view
#        JOIN program_requirements_old b ON a.program_requirements_id = b.id
#        WHERE program_id = ?
#    '''
#    df = pd.read_sql_query(query, q.app.conn, params=(program_id,))
#    major_records = df.to_dict('records')
#
#    query = 'SELECT * FROM program_requirements WHERE program_id = ?'
#    df = pd.read_sql_query(query, q.app.conn, params=(program_id,))
#    rows = df.to_dict('records')
#    row = rows[0]
#
#    if compare:
#        #width='50%'
#        location = 'horizontal'
#    else:
#        #width='100%'
#        location = 'vertical'
#
#    #await render_major_dashboard(q, title, row, 'middle_' + location)
#    #await render_major_table(q, major_records, 'bottom_' + location)

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

def dropdown_menus(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.inline(
                items=[
                    ui.dropdown(
                        name='degree', 
                        label='Degree', 
                        value=q.args.degree,
                        trigger=True,
                        width=menu_width,
                        choices=[
                            ui.choice(name='AS', label="Associate"),
                            ui.choice(name='BS', label="Bachelor's"),
                            ui.choice(name='MS', label="Master's"),
                            ui.choice(name='DC', label="Doctorate"),
                            ui.choice(name='UC', label="Undergraduate Certificate"),
                            ui.choice(name='GC', label="Graduate Certificate")
                    ]),
                    ui.dropdown(
                        name='area_of_study', 
                        label='Area of Study', 
                        value=q.args.area_of_study,
                        trigger=False,
                        disabled=False,
                        width=menu_width,
                        choices=[
                            ui.choice(name='BM', label='Business & Management'),
                            ui.choice(name='CS', label='Cybersecurity'),
                            ui.choice(name='DA', label='Data Analytics'),
                            ui.choice(name='ET', label='Education & Teaching'),
                            ui.choice(name='HS', label='Healthcare & Science'),
                            ui.choice(name='LA', label='Liberal Arts & Communications'),
                            ui.choice(name='PS', label='Public Safety'),
                            ui.choice(name='IT', label='IT & Computer Science')
                    ]),
                    ui.dropdown(
                        name='major', 
                        label='Major', 
                        value=q.args.major,
                        trigger=False,
                        disabled=False,
                        width=menu_width,
                        choices=[
                            ui.choice(name='AC', label='Accounting'),
                            ui.choice(name='BA', label='Business Administration'),
                            ui.choice(name='FI', label='Finance'),
                            ui.choice(name='HR', label='Human Resource Management'),
                            ui.choice(name='MS', label='Management Studies'),
                            ui.choice(name='MK', label='Marketing'),
                    ]),
                ]
            )
        ]
    )

query = '''
SELECT DISTINCT menu_area_id 
FROM menu_programs_by_areas
WHERE menu_degree_id = ?
ORDER BY menu_area_id
'''

def dropdown_menus_vertical(q, location='horizontal', demo=True):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='degree',
                label='Degree',
                value='BS' if demo else q.args.degree,
                trigger=True,
                width=menu_width,
                choices=[
                    ui.choice(name='AS', label="Associate"),
                    ui.choice(name='BS', label="Bachelor's"),
                    ui.choice(name='MS', label="Master's"),
                    ui.choice(name='DC', label="Doctorate"),
                    ui.choice(name='UC', label="Undergraduate Certificate"),
                    ui.choice(name='GC', label="Graduate Certificate")
            ]),
            ui.dropdown(
                name='area_of_study',
                label='Area of Study',
                value='BM' if demo else q.args.area_of_study,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=[
                    ui.choice(name='BM', label='Business & Management'),
                    ui.choice(name='CS', label='Cybersecurity'),
                    ui.choice(name='DA', label='Data Analytics'),
                    ui.choice(name='ET', label='Education & Teaching'),
                    ui.choice(name='HS', label='Healthcare & Science'),
                    ui.choice(name='LA', label='Liberal Arts & Communications'),
                    ui.choice(name='PS', label='Public Safety'),
                    ui.choice(name='IT', label='IT & Computer Science')
            ]),
            ui.dropdown(
                name='major',
                label='Major',
                value='BA' if demo else q.args.major,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=[
                    ui.choice(name='AC', label='Accounting'),
                    ui.choice(name='BA', label='Business Administration'),
                    ui.choice(name='FI', label='Finance'),
                    ui.choice(name='HR', label='Human Resource Management'),
                    ui.choice(name='MS', label='Management Studies'),
                    ui.choice(name='MK', label='Marketing'),
            ]),
        ]
    )

def dropdown_menus_vertical_compare(q, location='horizontal', demo=True):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='degree',
                label='Degree',
                #value=q.args.degree,
                value='BS' if demo else q.args.degree,
                trigger=True,
                width=menu_width,
                choices=[
                    ui.choice(name='AS', label="Associate"),
                    ui.choice(name='BS', label="Bachelor's"),
                    ui.choice(name='MS', label="Master's"),
                    ui.choice(name='DC', label="Doctorate"),
                    ui.choice(name='UC', label="Undergraduate Certificate"),
                    ui.choice(name='GC', label="Graduate Certificate")
            ]),
            ui.dropdown(
                name='area_of_study',
                label='Area of Study',
                value='BM' if demo else q.args.area_of_study,
                #value='BM',
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=[
                    ui.choice(name='BM', label='Business & Management'),
                    ui.choice(name='CS', label='Cybersecurity'),
                    ui.choice(name='DA', label='Data Analytics'),
                    ui.choice(name='ET', label='Education & Teaching'),
                    ui.choice(name='HS', label='Healthcare & Science'),
                    ui.choice(name='LA', label='Liberal Arts & Communications'),
                    ui.choice(name='PS', label='Public Safety'),
                    ui.choice(name='IT', label='IT & Computer Science')
            ]),
            ui.dropdown(
                name='major',
                label='Major',
                value='AC' if demo else q.args.major,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=[
                    ui.choice(name='AC', label='Accounting'),
                    ui.choice(name='BA', label='Business Administration'),
                    ui.choice(name='FI', label='Finance'),
                    ui.choice(name='HR', label='Human Resource Management'),
                    ui.choice(name='MS', label='Management Studies'),
                    ui.choice(name='MK', label='Marketing'),
            ]),
        ]
    )

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
meta = ui.meta_card(
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

footer = ui.footer_card(
    box='footer',
    caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
    '''
)

markdown = ui.form_card(
    box='leftnote',
    items=[ui.text(templates.sample_markdown)]
)

#def header_new_old(image_path, q):
#    result = ui.header_card(
#        box='header', 
#        title='UMGC Programs',
#        subtitle="Registration Assistant",
#        image=image_path,
#        secondary_items=[
#            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
#                ui.tab(name='#home', label='Home'),
#                ui.tab(name='#student', label='Student Info'),
#                ui.tab(name='#major', label='Major'),
#                ui.tab(name='#electives', label='Courses'),
#                ui.tab(name='#courses', label='Schedule'),
#            ]),
#        ],
##        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
#        items=[
#            ui.persona(title='John Doe', subtitle='Student', size='xs',
#                       image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
#        ]
#    )
#    return result

def get_header(image_path, q):
    persona_image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'
    commands = [
        ui.command(name='profile', label='Profile', icon='Contact'),
        ui.command(name='preferences', label='Preferences', icon='Settings'),
        ui.command(name='logout', label='Logout', icon='SignOut'),
    ]

    result = ui.header_card(
        box='header',
        title='UMGC',
        #title='',
        #subtitle='',
        subtitle="Registration Assistant",
        image=image_path,
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                ui.tab(name='#student', label='Student Info'),
                ui.tab(name='#major', label='Select Major'),
                ui.tab(name='#courses', label='Select Courses'),
                ui.tab(name='#schedule', label='Set Schedule'),
            ]),
        ],
        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
#        items=[ui.persona(title='John Doe', subtitle='Student', size='xs', image=persona_image)]
    )
    return result

#async def serve(q: Q):
#    if not q.client.initialized:
#        q.page['example'] = ui.form_card(box='1 1 2 3', items=[])
#        q.client.initialized = True
#    if 'profile' in q.args and not q.args.show_form:
#        q.page['example'].items = [
#            ui.text(f'profile={q.args.profile}'),
#            ui.text(f'preferences={q.args.preferences}'),
#            ui.text(f'logout={q.args.logout}'),
#            ui.button(name='show_form', label='Back', primary=True),
#        ]
#    else:
#        q.page['example'].items = [
#            ui.menu(image=image, items=commands),
#            ui.menu(icon='Add', items=commands),
#            ui.menu(label='App', items=commands),
#            ui.menu(items=commands)
#        ]
#    await q.page.save()

def d3plot(html, location='horizontal', height='500px', width='100%'):
    result = ui.frame_card(
        box=ui.box(location, height=height, width=width),
        title='Tentative Course Schedule',
        content=html
    )
    return result

def stats(D):
    return ui.form_card(
        box='horizontal', items=[
            ui.stats(justify='between', items=[
                ui.stat(label='Credits', 
                        value=str(D['total_credits_remaining']), 
                        caption='Credits Remaining', 
                        icon='LearningTools'),            
                ui.stat(label='Tuition', 
                        value=D['next_term_cost'], 
                        caption='Estimated Tuition', 
                        icon='Money'),
                ui.stat(label='Terms Remaining', 
                        value=str(D['terms_remaining']), 
                        caption='Terms Remaining', 
                        icon='Education'),
                ui.stat(label='Finish Date', 
                        value=D['completion_date'], 
                        caption='(Estimated)', 
                        icon='SpecialEvent'),
                ui.stat(label='Total Tuition', 
                        value=D['total_cost_remaining'], 
                        caption='Estimated Tuition', 
                        icon='Money'),
            ])
        ]
    )

#    q.page['tall_stats'] = ui.tall_stats_card(
##        box=ui.box('right2', height='200px',),
#        box=ui.box('left2'),
#        items=[
#            ui.stat(label='FINISH DATE', value=completion_date),
#            ui.stat(label='TERMS REMAINING', value=str(terms_remaining)),
#            ui.stat(label='CREDITS LEFT', value=str(total_credits_remaining)), 
#        ]
#    )