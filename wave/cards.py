from h2o_wave import ui
from typing import Optional, List
from utils import get_query, get_query_one
import pandas as pd
import sys

######################################################################
####################  STANDARD WAVE CARDS (START) ####################

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

footer = ui.footer_card(
    box='footer',
    caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
    '''
)
####################  STANDARD WAVE CARDS (END)   ####################
######################################################################

######################################################################
####################  SQL QUERIES & UTILITIES (START) ################

# These are used in app.py and elsewhere
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

def render_dialog_description(q, course):
    '''
    Display the description of a row clicked on a table
    '''
    df = q.client.program_df
    description = df.loc[df['course'] == course, 'description'].iloc[0]

    q.page['meta'].dialog = ui.dialog(
        name = 'view_description',
        title = course + ' Course Description',
        width = '480px',
        items = [ui.text(description)],
        closable = True,
        #events = ['dismissed']
    )

####################  SQL QUERIES & UTILITIES  (END)   ###############
######################################################################


##############################################################
####################  DEBUG CARDS (START) ####################

def render_debug_card(q, location='debug', width='33%', height='200px'):
    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

    '''
    return ui.markdown_card(
        box=ui.box(location, width=width, height=height), 
        title='Debugging Information', 
        content=content 
    )

def render_debug_client_card(q, location='debug', width='33%', height='200px'):
    content = f'''

### q.client value:
{q.client}

    '''
    return ui.markdown_card(
        ui.box(location, width=width, height=height), 
        title='Client Debugging Information', 
        content=content 
    )

def render_debug_user_card(q, location='debug', width='33%', height='200px'):
    content = f'''
### q.app values:
{q.app}

### q.user values:
{q.user}

    '''
    return ui.markdown_card(
        ui.box(location, width=width, height=height), 
        title='User Debugging Information', 
        content=content 
    )

def render_debug(q, location='debug', width='25%', height='230px'):
    add_card(q, 'debug_user_info', render_debug_user_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_info', render_debug_card(q, location=location, width=width, height=height)) 

####################  DEBUG CARDS (END)   ####################
##############################################################

##############################################################
####################  HOME PAGE (START)  #####################

yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
career_assessment_card = ui.wide_info_card(
    box=ui.box('bottom_horizontal', width='400px'),
    name='Assessments',
    icon='AccountActivity',
    title='Career Assessments',
    caption=f'Access career assessment tools like **UMGC CareerQuest** or add a page like <a href="{yale_url}" target="_blank">Yale\'s</a> with _Interest_, _Personality_, and _Skills_ assessments.'
)

ai_enablement_card = ui.wide_info_card(
    box=ui.box('bottom_horizontal', width='400px'),
    name='ai',
    icon='LightningBolt',
    title='AI Enablement',
    caption='*Interest* or *Skills* assessments critical for AI recommendations.'
)

####################  HOME PAGE (END)    #####################
##############################################################

##############################################################
####################  MAJORS PAGE (START) ####################

async def get_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
    return choices

async def render_dropdown_menus(q, location='top_horizontal', menu_width='280px'):
    #degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
    #area_query = '''
    #    SELECT DISTINCT menu_area_id AS name, area_name AS label
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ?
    #'''
    #program_query = '''
    #    SELECT program_id AS name, program_name AS label
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ? AND menu_area_id = ?
    #'''
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

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
    ui.tag(label='REQUIRED', color='$red'),
    ui.tag(label='GENERAL', color='#046A38'),
    ui.tag(label='MAJOR', color='#1565C0'),
]

async def render_program_dashboard(q, location, width):
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

async def render_program_dashboard_inline_to_fix(q, location, width):
    '''
    ** CURRENTLY DOES NOT WORK

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
                        items=[ui.inline(items=[
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
                        ])]
                )]
            ))
            #else:
            #    pass
            #    # send a warning

async def render_program(q, location='middle_vertical', width='100%', dashboard=True):
    async def _render_program_dashboard(q, location=location, width=width):
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
    async def _render_program_group(group_name, record_type, df, collapsed, check=True):
        '''
        group_name: 
        record_type: 
        df: course (Pandas) dataframe
        collapsed:
        check: If True, only return card if # rows > 0
            e.g., we will always return 'MAJOR' but not necessarily 'REQUIRED'
        '''
        # card will be returned if 
        # (1) check == False
        # (2) check == True and sum(rows) > 0
        any_rows = (df['type'].str.upper() == record_type).sum() > 0

        #if any_rows: #(check and not_blank) or (not check):
        card = ui.table_group(group_name, [
            ui.table_row(
                #name=str(row['id']),
                name=row['course'],
                cells=[
                    row['course'],
                    row['title'],
                    str(row['credits']),
                    row['type'].upper(),
                ]
            ) for _, row in df.iterrows() if row['type'].upper() == record_type
        ], collapsed=collapsed)
        return card

        #else:
        #    return ''
    async def _render_program_table(q, df, location='bottom_vertical', cardname='my_test_table', width='100%', 
        height='350px', ge=False, elective=False):
        '''
        q:
        df:
        location:
        cardname:
        width:
        height:
        ge: Include GE classes
        elective: Include Elective classes
        '''
        return add_card(q, cardname, ui.form_card(
            box=ui.box(location, height=height, width=width),
            items=[
                ui.text('Required Courses', size=ui.TextSize.L),
                ui.table(
                    name='program_table',
                    downloadable=False,
                    resettable=False,
                    groupable=False,
                    height=height,
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
                                tags=UMGC_tags
                            )
                        ),
                        ui.table_column(name='menu', label='Menu', max_width='150',
                            cell_type=ui.menu_table_cell_type(name='commands', commands=[
                                ui.command(name='view_description', label='Course Description'),
                                ui.command(name='prerequisites', label='Show Prerequisites'),
                        ]))
                    ],
                    groups=[
                        await _render_program_group(
                            'Required Major Core Courses',
                            'MAJOR',
                            df,
                            False,
                            check=True),
                        await _render_program_group(
                            'Required Related Courses/General Education',
                            'REQUIRED,GENERAL',
                            df,
                            True),
                        await _render_program_group(
                            'Required Related Courses/Electives',
                            'REQUIRED,ELECTIVE',
                            df,
                            True),
                        #await _render_program_group(
                        #    'General Education',
                        #    'GENERAL',
                        #    major_records,
                        #    True),
                        #await _render_program_group(
                        #    'Electives',
                        #    'ELECTIVE',
                        #    major_records,
                        #    True)
                # ui.text(title, size=ui.TextSize.L),
            ])]
        ))
    async def _render_program_coursework(q, location=location, table_height='350px'):
        '''
        Create program coursework requirement table
        '''
        #############
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
        q.client.program_df = df

        await _render_program_table(q, df, location, height=table_height)

    if dashboard:
        await _render_program_dashboard(q, location=location)
        table_height='350px'
    else:
        table_height='480px'
    await _render_program_coursework(q, location=location, table_height=table_height)

####################  MAJORS PAGE (END)   ####################
##############################################################

##############################################################
####################  GE PAGE (START) ########################

async def get_ge_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['name'] + ': ' + row['title']) for row in rows]
    return choices

ge_query = "SELECT name, name || ': ' || title AS label FROM ge_view WHERE ge_id=? ORDER BY name"
ge_query_nopre = '''
    SELECT name, name || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
        AND pre='' 
        AND pre_credits=''
    ORDER BY name
'''
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
            ui.inline([
                ui.text('Communications', size=ui.TextSize.XL),
                ui.checkbox(name='ge_comm_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_comm_1',
                label='1. WRTG 111 or another writing course (3 credits)',
                value=q.user.ge_comm_p1 if (q.user.ge_comm_p1 is not None) else 'WRTG 111',
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_2',
                label='2. WRTG 112 (3 credits)',
                value=q.user.ge_comm_p2 if (q.user.ge_comm_p2 is not None) else 'WRTG 112',
                disabled=False,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_3',
                label='3. Communication, writing, or speech course (3 credits)',
                placeholder='(Select One)',
                value=q.user.ge_comm_p3 if (q.user.ge_comm_p3 is not None) else q.args.ge_comm_p3,
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_4',
                label='4. Advanced writing course (3 credits)',
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
            ui.inline([
                ui.text('Mathematics', size=ui.TextSize.XL),
                ui.checkbox(name='ge_math_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_math',
                label='Mathematics (3 credits)',
                value=q.user.ge_math if (q.user.ge_math is not None) else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                required=True,
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
            ui.inline([
                ui.text('Arts and Humanities', size=ui.TextSize.XL),
                ui.checkbox(name='ge_arts_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_arts_1',
                label='1. Arts and Humanities (3 credits)',
                value=q.user.ge_arts_1 if (q.user.ge_arts_1 is not None) else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Arts and Humanities (3 credits)',
                value=q.user.ge_arts_2 if (q.user.ge_arts_2 is not None) else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(q, ge_query, (6,))
            ),
        ]
    )
    return card

async def render_ge_science_card(q, menu_width, location='grid'):
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=ui.box(location),
        items=[
            ui.inline([
                ui.text('Biological and Physical Sciences', size=ui.TextSize.XL),
                ui.checkbox(name='ge_science_check', label='')
            ], justify='between', align='start'),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            #ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='1. Lecture with Lab (4 credits): Select one',
                value=q.user.ge_bio_1a if (q.user.ge_bio_1a is not None) else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Combined Lecture and Laboratory)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (7,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                #label='Separate Lecture and Laboratory',
                value=q.user.ge_bio_1c if (q.user.ge_bio_1c is not None) else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Separate Lecture and Laboratory)',
                width=menu_width,
                choices=await get_choices(q, ge_pairs_query, ())
            ),
            ui.dropdown(
                name='ge_bio_1b',
                #label='For Science Majors and Minors only:',
                value=q.user.ge_bio_1b if (q.user.ge_bio_1b is not None) else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Science Majors and Minors only)',
                #placeholder='or (Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (8,))
            ),
            #ui.separator(label='Select an additional science course:'),
            #nopre=True # check for easy classes by selecting those w/o prerequisites
            ui.dropdown(
                name='ge_bio_2',
                label='2. An additional science course (3 credits)',
                value=q.user.ge_bio_2 if (q.user.ge_bio_2 is not None) else q.args.ge_bio_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query_nopre if nopre else ge_query, (10,))
                #choices=await get_choices(q, ge_query_nopre, (10,))
            ),
        ]
    )
    return card

async def render_ge_beh_card(q, menu_width, location='grid'):
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=ui.box(location),
        items=[
            #ui.separator(label=''),
            ui.inline([
                ui.text('Behavioral and Social Sciences', size=ui.TextSize.XL),
                ui.checkbox(name='ge_beh_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_beh_1',
                label='1. Behavioral and Social Sciences (3 credits)',
                value=q.user.ge_beh_1 if (q.user.ge_beh_1 is not None) else q.args.ge_beh_1,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                #choices=await get_choices(q, ge_query, (11,))
                choices=await get_choices(q, ge_query_nopre if nopre else ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Behavioral and Social Sciences (3 credits)',
                value=q.user.ge_beh_2 if (q.user.ge_beh_2 is not None) else q.args.ge_beh_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query_nopre if nopre else ge_query, (11,))
                #choices=await get_choices(q, ge_query, (11,))
            ),
        ]
    )
    return card

async def render_ge_research_card(q, menu_width, location='grid'):
    # make some defaults based on area of program chosen:
    if q.user.area_of_study == 1:
        q.user.ge_res_1 = 'PACE 111B'

    card = ui.form_card(
        box=ui.box(location),
        items=[
            ui.inline([
                ui.text('Research and Computing Literacy', size=ui.TextSize.XL),
                ui.checkbox(name='ge_res_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_res_1',
                label='1. Professional Exploration Course (3 credits)',
                value=q.user.ge_res_1 if (q.user.ge_res_1 is not None) else q.args.ge_res_1,
                # default value will depend on the major chosen
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(q, ge_query, (12,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills and Professional Development (1 credit)',
                value=q.user.ge_res_2 if (q.user.ge_res_2 is not None) else 'LIBS 150',
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (13,))
            ),
            ui.dropdown(
                name='ge_res_3',
                label='3. Computing or Information Technology (3 credits) One 3-credit course:',
                value=q.user.ge_res_3 if (q.user.ge_res_3 is not None) else q.args.ge_res_3,
                trigger=True,
                required=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,3))
            ),
           ui.dropdown(
                name='ge_res_3a',
                label='or three 1-credit courses:\n',
                required=True,
                value=q.user.ge_res_3a if (q.user.ge_res_3a is not None) else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                #label='Computing or Information Technology (1 credit)',
                value=q.user.ge_res_3b if (q.user.ge_res_3b is not None) else q.args.ge_res_3b,
                trigger=True,
                placeholder='and (Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                #label='Computing or Information Technology (1 credit each)',
                value=q.user.ge_res_3c if (q.user.ge_res_3c is not None) else q.args.ge_res_3c,
                trigger=True,
                placeholder='and (Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
        ]
    )
    return card

####################  GE PAGE (END)   ########################
##############################################################

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

###########

def d3plot(html, location='horizontal', height='500px', width='100%'):
    card = ui.frame_card(
        box=ui.box(location, height=height, width=width),
        title='Tentative Course Schedule',
        content=html
    )
    return card

