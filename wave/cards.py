from h2o_wave import ui
from typing import Optional, List
from utils import get_query, get_query_one
import pandas as pd
import sys

async def get_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
    return choices

async def get_ge_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['name'] + ': ' + row['title']) for row in rows]
    return choices

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)

def meta_card():
    card = ui.meta_card(
        box='', 
        themes=[ui.theme( # UMGC red: '#a30606', UMGC yellow: '#fdbf38'
            name='UMGC',
            primary='#a30606', 
            text='#000000',
            card='#ffffff',
            page='#e2e2e2', 
        )],
        theme='UMGC',
        title='UMGC Wave App',
        layouts=[ui.layout(
            breakpoint='xs', 
            min_height='100vh', 
            zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
                    ui.zone('top_vertical'),
                    ui.zone('middle_horizontal', direction=ui.ZoneDirection.ROW),
                    ui.zone('middle_vertical'),
                    #ui.zone('vertical'),                                   # delete eventually
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'), # delete eventually
                    ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
                    ui.zone('bottom_vertical'),
                    ui.zone('debug', direction=ui.ZoneDirection.ROW), 
                ]),
                ui.zone('footer'),
    ])])
    return card 

def header_card(q):
    card = ui.header_card(
        box='header', 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                #ui.tab(name='#student', label='Student Info'),
                ui.tab(name='#major', label='Major'), # 'Select Major'
                ui.tab(name='#course', label='Course'), # 'Select Courses'
                ui.tab(name='#ge', label='GE'), # 'Select Courses'
                ui.tab(name='#electives', label='Electives'), # 'Select Courses'
                ui.tab(name='#schedule', label='Schedule'), # 'Set Schedule'
            ]),
        ],
        items=[
            ui.textbox(
                name='textbox_default', 
                label='Student Name', 
                value='John Doe', 
                disabled=True
        )],
    )
    return card

degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
area_query = '''
    SELECT DISTINCT menu_area_id AS name, area_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ?
'''
program_query = '''
    SELECT program_id AS name, program_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''

    #states = [
    #    ('q.app', q.app),
    #    ('q.user', q.user),
    #    ('q.client', q.client),
    #    ('q.events', q.events),
    #    ('q.args', q.args)
    #]

def render_debug_card(q, location='debug', width='33%'):
    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

    '''
    return ui.markdown_card(
        box=ui.box(location, width=width), 
        title='Debugging Information', 
        content=content 
    )

def render_debug_client_card(q, location='debug', width='33%'):
    content = f'''

### q.client value:
{q.client}

    '''
    return ui.markdown_card(
        ui.box(location, width=width), 
        title='Client Debugging Information', 
        content=content 
    )

def render_debug_user_card(q, location='debug', width='33%'):
    content = f'''
### q.app values:
{q.app}

### q.user values:
{q.user}

    '''
    return ui.markdown_card(
        ui.box(location, width=width), 
        title='User Debugging Information', 
        content=content 
    )

def render_debug(q, location='debug', width='25%'):
    add_card(q, 'debug_user_info', render_debug_user_card(q,  location=location, width=width)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q,  location=location, width=width)) 
    add_card(q, 'debug_info', render_debug_card(q, location=location, width=width)) 

def render_home_cards(q, location='top_horizontal', width='25%'):
    add_card(q, 'student_guest', ui.wide_info_card(
        box=ui.box(location, width=width),
        name='',
        icon='Contact',
        title='Guests',
        caption='Login not required to use this app.'
    ))
    add_card(q, 'login',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='login',
            title='Login',
            caption='User roles: *admin*, *coach*, *student*, *prospect*.',
            icon='Signin')
    )
    add_card(q, 'import',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='import',
            title='Import',
            caption='Future state: Import UMGC student info.',
            icon='Import')
    )
    add_card(q, 'personalize',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='person',
            title='Personalize',
            caption='User adds new info or confirms imported info.',
            icon='UserFollowed')
    )

def render_major_recommendation_card(q, location='top_horizontal', width='350px'):
    card = ui.form_card(
        box=ui.box(location, width=width),
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
            ui.inline(
                items=[
                    ui.button(name='show_recommendations', label='Submit', primary=True),
                    ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
                ]
            )
        ]
    )
    return card

async def render_dropdown_menus_old(q, location='top_horizontal', menu_width='280px'):
    degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
    area_query = '''
        SELECT DISTINCT menu_area_id AS name, area_name AS label
        FROM menu_all_view 
        WHERE menu_degree_id = ?
    '''
    program_query = '''
        SELECT program_id AS name, program_name AS label
        FROM menu_all_view 
        WHERE menu_degree_id = ? AND menu_area_id = ?
    '''
    card = ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='degree',
                label='Degree',
                value=q.client.degree if (q.client.degree is not None) else q.args.degree,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, degree_query)
            ),
            ui.dropdown(
                name='area_of_study',
                label='Area of Study',
                value=q.client.area_of_study if (q.client.area_of_study is not None) else \
                    q.args.area_of_study,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=None if (q.client.degree is None) else \
                    await get_choices(q, area_query, (q.client.degree,))
            ),
            ui.dropdown(
                name='program',
                label='Program',
                value=q.client.program if (q.client.program is not None) else q.args.program,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=None if (q.client.area_of_study is None) else \
                    await get_choices(q, program_query, (q.client.degree, q.client.area_of_study))
            )
        ]
    )
    return card

async def render_dropdown_menus(q, location='top_horizontal', menu_width='280px'):
    degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
    area_query = '''
        SELECT DISTINCT menu_area_id AS name, area_name AS label
        FROM menu_all_view 
        WHERE menu_degree_id = ?
    '''
    program_query = '''
        SELECT program_id AS name, program_name AS label
        FROM menu_all_view 
        WHERE menu_degree_id = ? AND menu_area_id = ?
    '''
    card = ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='degree',
                label='Degree',
                value=q.user.degree if (q.user.degree is not None) else q.args.degree,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, degree_query)
            ),
            ui.dropdown(
                name='area_of_study',
                label='Area of Study',
                value=q.user.area_of_study if (q.user.area_of_study is not None) else \
                    q.args.area_of_study,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=None if (q.user.degree is None) else \
                    await get_choices(q, area_query, (q.user.degree,))
            ),
            ui.dropdown(
                name='program',
                label='Program',
                value=q.user.program if (q.user.program is not None) else q.args.program,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=None if (q.user.area_of_study is None) else \
                    await get_choices(q, program_query, (q.user.degree, q.user.area_of_study))
            )
        ]
    )
    return card


warning_example_card = ui.form_card(
    box='1 1 4 7',
    items=[
        ui.message_bar(type='blocked', text='This action is blocked.'),
        ui.message_bar(type='error', text='This is an error message'),
        ui.message_bar(type='warning', text='This is a warning message.'),
        ui.message_bar(type='info', text='This is an information message.'),
        ui.message_bar(type='success', text='This is an success message.'),
        ui.message_bar(type='danger', text='This is a danger message.'),
        ui.message_bar(type='success', text='This is a **MARKDOWN** _message_.'),
        ui.message_bar(type='success', text='This is an <b>HTML</b> <i>message</i>.'),
    ]
)

footer = ui.footer_card(
    box='footer',
    caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
    '''
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

async def render_major_table(q, records, location='bottom_vertical', cardname='my_test_table', width='100%', ge=False, elective=False):
    def _render_major_table_group(group_name, record_type, records, collapsed):
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

    return add_card(q, cardname, ui.form_card(
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
                    ]))
                ],
                groups=[
                    _render_major_table_group(
                        'Required Major Core Courses',
                        'MAJOR',
                        records,
                        True),
                    _render_major_table_group(
                        'Required Related Courses/General Education',
                        'REQUIRED,GENERAL',
                        records,
                        True),
                    _render_major_table_group(
                        'Required Related Courses/Electives',
                        'REQUIRED,ELECTIVE',
                        records,
                        True),
                    #_render_major_table_group(
                    #    'General Education',
                    #    'GENERAL',
                    #    major_records,
                    #    True),
                    #_render_major_table_group(
                    #    'Electives',
                    #    'ELECTIVE',
                    #    major_records,
                    #    True)
            # ui.text(title, size=ui.TextSize.L),
        ])]
    ))

async def render_majors_coursework(q, location='bottom_vertical'):
    '''
    Create major coursework requirement table
    '''
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
    df = pd.read_sql_query(query, q.user.conn, params=(q.user.program_id,))
    major_records = df.to_dict('records')
    q.user.major_coursework_df = df
    
    await render_major_table(q, major_records, location)

async def render_majors_coursework_new(q, location='bottom_vertical'):
    '''
    Create major coursework requirement table
    '''
    if not q.user.major_coursework_df:
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
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.program_id,))
        q.user.major_coursework_df = df

    major_records = q.user.major_coursework_df.to_dict('records')    
    await render_major_table(q, major_records, location)

async def render_majors(q, location='middle_vertical', width='100%'):

    async def _render_major_dashboard(q, location=location, width=width):
        '''
        Renders the dashboard with explored majors
        :param q: instance of Q for wave query
        :param location: page location to display
        '''
        title = q.user.degree_program # program name
 
        if q.user.degree == '2':
            # get program summary for bachelor's degrees
            query = 'SELECT * FROM program_requirements WHERE program_id = ?'
            row = await get_query_one(q, query, params=(q.user.program_id,))

            if row:
                return add_card(q, 'major_dashboard', ui.form_card(
                    box=ui.box(location, width=width),
                    items=[
                        ui.text(title + ': Credits', size=ui.TextSize.L),
                        ui.stats(
                            # justify='between',
                            items=[
                                ui.stat(
                                    label='Major',
                                    value=str(row['major']),
                                    caption='Required Core',
                                    icon='Trackers'),
                                ui.stat(
                                    label='Required',
                                    value=str(row['related_ge'] + row['related_elective']),
                                    caption='Required Related',
                                    icon='News'),
                                ui.stat(
                                    label='General Education',
                                    value=str(row['remaining_ge']),
                                    caption='Remaining GE',
                                    icon='TestBeaker'),
                                ui.stat(
                                    label='Elective',
                                    value=str(row['remaining_elective']),
                                    caption='Remaining Elective',
                                    icon='Media'),
                                ui.stat(
                                    label='TOTAL',
                                    value=str(row['total']),
                                    caption='Total Credits',
                                    icon='Education'),
                        ])
                ]))
            #else:
            #    pass
            #    # send a warning
    async def _render_major_coursework(q, location=location):
        '''
        Create major coursework requirement table
        '''
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
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.program_id,))
        major_records = df.to_dict('records')
        q.user.major_coursework_df = df

        await render_major_table(q, major_records, location)

    await _render_major_dashboard(q, location=location)
    await _render_major_coursework(q, location=location)

def d3plot(html, location='horizontal', height='500px', width='100%'):
    card = ui.frame_card(
        box=ui.box(location, height=height, width=width),
        title='Tentative Course Schedule',
        content=html
    )
    return card

async def render_major_dashboard(q, location='middle_vertical', width='100%'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    '''

    title = q.user.degree_program # program name
 
    if q.user.degree == '2':
        # get program summary for bachelor's degrees
        query = 'SELECT * FROM program_requirements WHERE program_id = ?'
        row = await get_query_one(q, query, params=(q.user.program_id,))

        if row:
            return add_card(q, 'major_dashboard', ui.form_card(
                box=ui.box(location, width=width),
                items=[
                    ui.text(title + ': Credits', size=ui.TextSize.L),
                    ui.stats(
                        # justify='between',
                        items=[
                            ui.stat(
                                label='Major',
                                value=str(row['major']),
                                caption='Required Core',
                                icon='Trackers'),
                            ui.stat(
                                label='Required',
                                value=str(row['related_ge'] + row['related_elective']),
                                caption='Required Related',
                                icon='News'),
                            ui.stat(
                                label='General Education',
                                value=str(row['remaining_ge']),
                                caption='Remaining GE',
                                icon='TestBeaker'),
                            ui.stat(
                                label='Elective',
                                value=str(row['remaining_elective']),
                                caption='Remaining Elective',
                                icon='Media'),
                            ui.stat(
                                label='TOTAL',
                                value=str(row['total']),
                                caption='Total Credits',
                                icon='Education'),
                    ])
            ]))
        #else:
        #    pass
        #    # send a warning

ge_query = "SELECT name, name || ': ' || title AS label FROM ge_view WHERE ge_id=? ORDER BY name"
ge_credits_query = '''
    SELECT name, name || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? AND credits=? 
    ORDER BY name
'''
ge_pairs_query = '''
    SELECT 
        name, 
        name || ' & ' || substr(note, 27, 3) || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=9 AND credits=3
    ORDER BY name
'''

async def render_ge_comm_card(q, menu_width, location='grid'):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            ui.text('Communications', size=ui.TextSize.XL),
            ui.dropdown(
                name='ge_comm_p1',
                label='1. WRTG 111 or another writing course',
                value=q.user.ge_comm_p1 if (q.user.ge_comm_p1 is not None) else 'WRTG 111',
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_p2',
                label='2. WRTG 112',
                value=q.user.ge_comm_p2 if (q.user.ge_comm_p2 is not None) else 'WRTG 112',
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_p3',
                label='3. A course in communication, writing, or speech',
                placeholder='(Select One)',
                value=q.user.ge_comm_p3 if (q.user.ge_comm_p3 is not None) else q.args.ge_comm_p3,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_p4',
                label='4. An upper-level advanced writing course',
                placeholder='(Select One)',
                value=q.user.ge_comm_p4 if (q.user.ge_comm_p4 is not None) else q.args.ge_comm_p4,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (4,))
            ),
        ]
    )
    return card

async def render_ge_math_card(q, menu_width, location='grid'):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            ui.text('Mathematics', size=ui.TextSize.XL),
            ui.dropdown(
                name='ge_math',
                label='Mathematics (3 credits)',
                value=q.user.ge_math if (q.user.ge_math is not None) else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (5,))
            ),
        ]
    )
    return card

async def render_ge_arts_card(q, menu_width, location='grid'):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            #ui.separator(label=''),
            ui.text('Arts and Humanities', size=ui.TextSize.XL),
            ui.dropdown(
                name='ge_arts_1',
                label='1. Arts and Humanities (3 credits)',
                value=q.user.ge_arts_1 if (q.user.ge_arts_1 is not None) else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Arts and Humanities (3 credits)',
                value=q.user.ge_arts_2 if (q.user.ge_arts_2 is not None) else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(q, ge_query, (6,))
            ),
        ]
    )
    return card

async def render_ge_science_card(q, menu_width, location='grid'):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            ui.text('Biological and Physical Sciences', size=ui.TextSize.XL),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='Lecture with Laboratory (4 credits)',
                value=q.user.ge_bio_1a if (q.user.ge_bio_1a is not None) else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (7,))
            ),
            ui.dropdown(
                name='ge_bio_1b',
                label='Lecture with Laboratory for Science Majors',
                value=q.user.ge_bio_1b if (q.user.ge_bio_1b is not None) else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (8,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                label='Separate Lecture and Laboratory',
                value=q.user.ge_bio_1c if (q.user.ge_bio_1c is not None) else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Select Pair)',
                width=menu_width,
                choices=await get_choices(q, ge_pairs_query, ())
            ),
            ui.separator(label='Select an additional science course:'),
            ui.dropdown(
                name='ge_bio_2',
                label='2. Any other science course (3 credits)',
                value=q.user.ge_bio_2 if (q.user.ge_bio_2 is not None) else q.args.ge_bio_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (10,))
            ),
        ]
    )
    return card

async def render_ge_beh_card(q, menu_width, location='grid'):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            #ui.separator(label=''),
            ui.text('Behavioral and Social Sciences', size=ui.TextSize.XL),
            ui.dropdown(
                name='ge_beh_1',
                label='1. Behavioral and Social Sciences (3 credits)',
                value=q.user.ge_beh_1 if (q.user.ge_beh_1 is not None) else q.args.ge_beh_1,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Behavioral and Social Sciences (3 credits)',
                value=q.user.ge_beh_2 if (q.user.ge_beh_2 is not None) else q.args.ge_beh_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (11,))
            ),
        ]
    )
    return card

async def render_ge_research_card(q, menu_width, location='grid'):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            ui.text('Research and Computing Literacy', size=ui.TextSize.XL),
            ui.dropdown(
                name='ge_res_1',
                label='1. Professional Exploration Course (3 credits)',
                value=q.user.ge_res_1 if (q.user.ge_res_1 is not None) else q.args.ge_res_1,
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(q, ge_query, (12,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills and Professional Development (1 credit)',
                value=q.user.ge_res_2 if (q.user.ge_res_2 is not None) else q.args.ge_res_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (13,))
            ),
            #ui.separator(),
            ui.text('**3. Select one 3-credit course:**'),
            ui.dropdown(
                name='ge_res_3',
                label='Computing or Information Technology (3 credits)',
                value=q.user.ge_res_3 if (q.user.ge_res_3 is not None) else q.args.ge_res_3,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,3))
            ),
            ui.text('**or three one-credit courses:**'),
            ui.dropdown(
                name='ge_res_3a',
                label='Computing or Information Technology (1 credit)',
                value=q.user.ge_res_3a if (q.user.ge_res_3a is not None) else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                label='Computing or Information Technology (1 credit)',
                value=q.user.ge_res_3b if (q.user.ge_res_3b is not None) else q.args.ge_res_3b,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                label='Computing or Information Technology (1 credit)',
                value=q.user.ge_res_3c if (q.user.ge_res_3c is not None) else q.args.ge_res_3c,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
        ]
    )
    return card
