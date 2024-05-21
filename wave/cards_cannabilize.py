from h2o_wave import ui
from typing import Optional, List

import utils
from utils import add_card, clear_cards
from utils import get_query, get_query_one, get_query_dict, get_query_df
from utils import get_choices, get_choices_with_disabled, get_role, \
    get_ge_choices, get_catalog_program_sequence, get_student_progress_d3
from utils import generate_periods, update_periods, generate_schedule, handle_prerequisites, \
    schedule_courses_old, update_courses, move_courses_forward
import pandas as pd
import sys

######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################


######################################################################
####################  SQL QUERIES & UTILITIES  #######################
######################################################################

# These queries are used in app.py for menus and in render_dropdown_menus_horizontal below

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

# To do: This is broken now. 
# Also, the 'dismissed' function does not work completely
# Card reappears when going to new page
def render_description_dialog_old(q, course):
    '''
    Display the description of a row clicked on a table
    '''
    df = q.user.student_info['df']['required']
    description = df.loc[df['course'] == course, 'description'].iloc[0]

    q.page['meta'].dialog = ui.dialog(
        name = 'view_description',
        title = course + ' Course Description',
        width = '480px',
        items = [ui.text(description)],
        closable = True,
        events = ['dismissed']
    )

def render_description_dialog(q, course, events=False):
    '''
    Display the description of a row clicked on a table
    df: dataframe from which the wave table was built
    course: course for description
    '''
    df = q.user.student_info['df']['required']

    #    # create the required course_dict once instead of every time this is called
    #    if 'course_dict' in q.user.student_info and q.user.student_info.get('course_dict') is not None:
    #        course_dict =  q.user.student_info['course_dict']
    #    else:
    #        # Assuming my_dict is your DataFrame converted to a dictionary of records
    #        tmp_dict = df.to_dict(orient='records')
    #        # Create a dictionary of dictionaries with 'course' as keys
    #        course_dict = {record['course']: record for record in tmp_dict}
    #        q.user.student_info['course_dict'] = course_dict
    #
    #    description = course_dict[course]['description']

    #an error crept into the df code so working direcdtly with dictionaries instead
    description = df.loc[df['course'] == course, 'description'].iloc[0]

    q.client.dialog_state = {
        'name': 'view_description',
        'title': course + ' Course Description',
        'width': '480px',
        'items': [ui.text(description)],
        'closable': True,
        #'events': ['dismissed']  # Changed from 'dismiss_dialog' to 'dismissed'
    }
    if events:
        q.client.dialog_state['events'] = ['dismissed']

    q.page['meta'].dialog = ui.dialog(**q.client.dialog_state)


##############################################################
####################  DEBUG CARDS (START) ####################
##############################################################

def render_debug_card_old(q, location='debug', width='33%', height='200px'):
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

def render_debug_user_card(q, flex=False, box='2 2 3 3', location='debug', width='33%', height='200px'):
    if flex:
        box = ui.box(location, width=width, height=height)
    content = f'''

### q.user values:
{q.user}

    '''
    return ui.markdown_card(
        box=box, 
        title='User Debugging Information', 
        content=content 
    )

def render_debug_app_card(q, flex=False, box='2 2 3 3', location='debug', width='33%', height='200px'):
    if flex:
        box = ui.box(location, width=width, height=height)
    content = f'''
### q.app values:
{q.app}

    '''
    return ui.markdown_card(
        box=box, 
        title='App Debugging Information', 
        content=content 
    )

def render_debug(q, location='debug', width='25%', height='230px'):
    add_card(q, 'debug_user_info', render_debug_user_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_info', render_debug_card(q, location=location, width=width, height=height)) 

##############################################################
####################  DEBUG CARDS (END)   ####################
##############################################################

##############################################################
####################  HOME PAGE  #############################
##############################################################

def render_welcome_card_old(q, box='1 2 7 1'):
    add_card(q, 'welcome_home', ui.form_card(
        box=box,
        items=[
            ui.text_l('Welcome to the UMGC Registration Assistant'),
            ui.text('(The Home page will collect student information)')
        ]
    ))

def render_welcome_card(q, box='1 2 4 1'):
    add_card(q, 'welcome_home', ui.form_card(
        box=box,
        items=[
            ui.text_l('Welcome to the UMGC Registration Assistant'),
            #ui.text('We will guide you through this experience.')
        ]
    ))

def render_please_login(q, box='5 2 3 1'):
    add_card(q, 'please_login', ui.form_card(
        box=box,
        items=[
            ui.text('You are a **Guest**. Login to save your information.'),
            #ui.text('We will guide you through this experience.')
        ]
    ))

def render_welcome_back_card(q, flex=True, location='vertical', box='1 3 3 3', title=''):
    student_info = q.user.student_info
    if flex:
        box = location
    content = f'''## Welcome back, {student_info['name']}.

### Here is your current selected student information:

- **Residency status**: {student_info['resident_status']}

- **Student type**: {student_info['student_profile']}

- **Transfer credits**: {student_info['transfer_credits']==1}

- **Financial aid**: {student_info['financial_aid']==1}

- **Selected program**: {student_info['degree_program']}

'''
    
    add_card(q, 'user_info',
        ui.markdown_card(
            box=box,
            title=title,
            content=content
        )
    )
    #add_card(q, 'user_info', 
    #    ui.form_card(
    #        box=box,
    #        items=[
    #            content,
    #            ui.inline(
    #                items=[
    #                    ui.button(name='show_recommendations', label='Submit', primary=True),
    #                    ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
    #                ]
    #            )
    #        ]
    #    )
    #)

def render_student_information_stub_card(box='1 1 2 2', flex=False, location='bottom_horizontal'):
    if flex:
        box=ui.box(location, width='400px')
    caption=f'Gather incomplete student information. Walk students through transfer credits. Access allowable data from UMGC servers.'
    card = ui.wide_info_card(
        box=box,
        name='StudentAssessments',
        icon='AccountActivity',
        title='Guided Student Updates',
        caption=caption
    )
    return card

def render_career_assessment_card(box='1 1 2 2', flex=True, location='horizontal'):
    if flex:
        box=ui.box(location, width='400px')
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Access career assessment tools like **UMGC CareerQuest** or add a page like <a href="{yale_url}" target="_blank">Yale\'s</a> with _Interest_, _Personality_, and _Skills_ assessments.'
    card = ui.wide_info_card(
        box=box,
        name='Assessments',
        icon='AccountActivity',
        title='Career Assessments',
        caption=caption
    )
    return card

def render_ai_enablement_card(box='1 1 2 2', flex=False, location='bottom_horizontal'):
    if flex:
        box=ui.box('bottom_horizontal', width='400px')
    card = ui.wide_info_card(
        box=box,
        name='ai',
        icon='LightningBolt',
        title='AI Enablement',
        caption='*Interest* or *Skills* assessments critical for AI recommendations.'
    )
    return card

##############################################################
####################  HOME PAGE (END)    #####################
##############################################################

##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################

async def render_dropdown_menus_horizontal(q, box='1 2 6 1', location='top_horizontal', flex=False, menu_width='280px'):
    '''
    Create menus for selecting degree, area of study, and program
    '''
    timedConnection = q.user.conn

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

    disabled = []

    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(q.user.student_info['menu']['degree']) if \
                (q.user.student_info['menu']['degree'] is not None) else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices=await get_choices(timedConnection, degree_query)
        ),
        ui.dropdown(
            name='menu_area',
            label='Area of Study',
            value=str(q.user.student_info['menu']['area_of_study']) if \
                (str(q.user.student_info['menu']['area_of_study']) is not None) else \
                str(q.args.menu_area),
            trigger=True,
            disabled=False,
            width='250px',
            choices=None if (q.user.student_info['menu']['degree'] is None) else \
                await get_choices(timedConnection, area_query, (q.user.student_info['menu']['degree'],))
        ),
        ui.dropdown(
            name='menu_program',
            label='Program',
            value=str(q.user.student_info['menu']['program']) if \
                (q.user.student_info['menu']['program'] is not None) else q.args.menu_program,
            trigger=True,
            disabled=False,
            width='300px',
            choices=None if (q.user.student_info['menu']['area_of_study'] is None) else \
                await get_choices_with_disabled(timedConnection, program_query, 
                (q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study']))
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='program', label='Save Program'),
            ui.command(name='classes_menu', label='Classes', 
                items=[
                    ui.command(name='add_ge', label='Add GE'),
                    ui.command(name='add_elective', label='Add Electives'),  
            ])
    ])

    if flex:
        box = location

    card = ui.form_card(box=box,
        items=[
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
        
    return card

    ########################

def render_major_recommendation_card(q, box='1 5 3 3', flex=False, location='top_horizontal', width='350px'):
    if flex:
        box=ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.choice_group(
                name='recommendation_group',
                label='Recommend a major based on ...',
                choices=[
                    ui.choice('A', label='My interests'),
                    ui.choice('B', label='My skills'),
                    ui.choice('C', label='Students like me'),
                    ui.choice('D', label='Shortest time to graduate'),
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
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

async def render_program_description(q, box):
    '''
    Renders the program description in an article card
    :param q: instance of Q for wave query
    :param location: page location to display
    '''
    timedConnection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    query = '''
        SELECT description, info, learn, certification
        FROM program_descriptions WHERE program_id = ?
    '''
    row = await get_query_one(timedConnection, query, params=(q.user.student_info['program_id'],))
    if row:
        # major = '\n##' + title + '\n\n'
        frontstuff = "\n\n#### What You'll Learn\nThrough your coursework, you will learn how to\n"
        if int(q.user.student_info['program_id']) in (4, 24, 29):
            content = row['info'] + '\n\n' + row['description']
        else:
            content = row['description'] + frontstuff + row['learn'] #+ '\n\n' + row['certification']

        card = add_card(q, 'program_description', ui.markdown_card(
            box=box, 
            title=title,
            content=content
        ))
        #card = add_card(q, 'program_description', ui.article_card(
        #    box=box, 
        #    title=title,
        ##    content=row['description'] + row['']
        #    content=content
        #))
        return card

async def render_program_dashboard(q, box):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    timedConnection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    #if q.user.student_info['menu_degree'] == '2':

    # get program summary for bachelor's degrees
    query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    row = await get_query_one(timedConnection, query, params=(q.user.student_info['program_id'],))
    if row:
        card = add_card(q, 'major_dashboard', ui.form_card(
            box=box,
            items=[
                #ui.text(title + ': Credits', size=ui.TextSize.L),
                ui.text('Credits', size=ui.TextSize.L),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Major',
                            value=str(row['major']),
                            #caption='Credits',
                            icon='Trackers',
                            icon_color='#135f96'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Required Related',
                            value=str(row['related_ge'] + row['related_elective']),
                            #caption='Credits',
                            icon='News',
                            icon_color='#a30606'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='General Education',
                            value=str(row['remaining_ge']),
                            #caption='Remaining GE',
                            icon='TestBeaker',
                            #icon_color='#787800'
                            icon_color='#3c3c43'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Elective',
                            value=str(row['remaining_elective']),
                            #caption='Remaining Elective',
                            icon='Media',
                            icon_color='#fdbf38'
                    )]
                ),
                ui.separator(),
                ui.stats(
                    items=[
                        ui.stat(
                            label='TOTAL',
                            value=str(row['total']),
                            #caption='Remaining Elective',
                            icon='Education',
                            icon_color='#da1a32 '
                    )]
                ),
            ])
        )
        return card
        #else: '#3c3c43' 
        #    pass
        #    # send a warning

async def _render_program_table(q, box=None, location=None, width=None, height=None, flex=False, check=True, ge=False, elective=False):
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
    df = q.user.student_info['df']['required']

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
        no_rows = (df['type'].str.upper() == record_type).sum() == 0

        if check and no_rows: #(check and not_blank) or (not check):
            return ''
        else:
            return ui.table_group(group_name, [
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

    # Create groups with logic
    groups = []
    result = await _render_program_group(
        'Required Major Core Courses',
        'MAJOR',
        df, collapsed=True, check=False
    )
    if result != '':
        groups.append(result)
        
    result = await _render_program_group(
        'Required Related Courses/General Education',
        'REQUIRED,GENERAL',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)
    
    result = await _render_program_group(
        'Required Related Courses/Electives',
        'REQUIRED,ELECTIVE',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)

    if ge:
        result = await _render_program_group(
            'General Education',
            'GENERAL',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)
        
    if elective:
        result = await _render_program_group(
            'Electives',
            'ELECTIVE',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)

    columns = [
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
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    #ui.command(name='prerequisites', label='Show Prerequisites'),
                ]
        ))
    ]

    if flex:
        box = ui.box(location, height=height, width=width)

    #title = q.user.student_info['degree_program'] + ': Explore Required Courses'
    title = 'Explore Required Courses'
    card = add_card(q, 'program_table_card', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='describe_program', label='About', 
                    #caption='Description', 
                    primary=True, disabled=True)
            ]),
            ui.table(
                name='program_table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height=height,
                columns=columns,
                groups=groups
            )
        ]
    ))
    return card

async def render_program_coursework_table(q, box='1 3 5 7', location='middle_vertical', width='100%', height='500px', flex=False):
    '''
    Create program coursework requirement table
    '''
    timedConnection = q.user.conn
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
    df = await get_query_df(timedConnection, query, params=(q.user.student_info['program_id'],))
    q.user.student_info['df']['required'] = df

    await _render_program_table(q, box=box, location=location, width=width, height=height, flex=flex)

async def render_program(q):
    await render_program_description(q, box='1 3 7 2')
    await render_program_dashboard(q, box='7 5 1 5')
    await render_program_coursework_table(q, box='1 5 6 5')

##############################################################
####################  PROGRAM PAGE (END)   ###################
##############################################################

##############################################################
####################  COURSES PAGE  ##########################
##############################################################

def render_courses_header(q, box='1 2 7 1'):
    degree_program = q.user.student_info['degree_program']
    content=f'**Program Selected**: {degree_program}'
    add_card(q, 'courses_header', ui.form_card(
        box=box,
        items=[
            ui.text_l(content),
            #ui.text('We will guide you through this experience.')
        ]
    ))

async def render_course_page_table(q, df, box=None, location=None, width=None, height=None, flex=False, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    df:
    location:
    cardname:
    width:
    height:
    '''
    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300', cell_overflow='wrap'),
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
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='show_prereq', label='Show Prerequisites'),
                    ui.command(name='select_elective', label='Select Elective'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)
    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='schedule_coursework', label='Schedule', 
                    #caption='Description', 
                    primary=True, disabled=False)
            ]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

##############################################################
####################  COURSES PAGE (END)  ####################
##############################################################

##############################################################
####################  GE PAGE (START) ########################
##############################################################

# reset ge defaults if covered in  

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

async def render_ge_arts_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    '''
    Create the General Education - Arts card
    '''
    timedConnection = q.user.conn
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Arts and Humanities', size=ui.TextSize.L),
                ui.checkbox(name='ge_arts_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_arts_1',
                label='1. Course (3 credits)',
                value=q.user.student_info['ge']['arts']['1'] if (q.user.student_info['ge']['arts']['1'] is not None) \
                    else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Course (3 credits)',
                value=q.user.student_info['ge']['arts']['2'] if (q.user.student_info['ge']['arts']['2'] is not None) \
                    else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(timedConnection, ge_query, (6,))
            ),
        ]
    )
    return card

async def render_ge_beh_card(q, menu_width, box='1 3 3 4', flex=False, location='grid'):
    '''
    Create the General Education - Behavioral and Social Sciences card
    '''
    timedConnection = q.user.conn
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=box,
        items=[
            #ui.separator(label=''),
            ui.inline([
                ui.text('Behavioral and Social Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_beh_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_beh_1',
                label='1. Course (3 credits)',
                value=q.user.student_info['ge']['beh']['1'] if (q.user.student_info['ge']['beh']['1'] is not None) \
                    else q.args.ge_beh_1,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (11,))
                #choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Course (3 credits)',
                value=q.user.student_info['ge']['beh']['2'] if (q.user.student_info['ge']['beh']['2'] is not None) \
                    else q.args.ge_beh_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (11,))
#                choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (11,))
            ),
        ]
    )
    return card

async def render_ge_bio_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    '''
    Create the General Education - Science card
    '''
    timedConnection = q.user.conn
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Biological and Physical Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_bio_check', label='')
            ], justify='between', align='start'),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            #ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='1. Lecture & Lab (4 credits): Select one',
                value=q.user.student_info['ge']['bio']['1a'] if (q.user.student_info['ge']['bio']['1a'] is not None) \
                    else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Combined Lecture & Lab)',
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (7,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                #label='Separate Lecture and Laboratory',
                value=q.user.student_info['ge']['bio']['1c'] if (q.user.student_info['ge']['bio']['1c'] is not None) \
                    else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Separate Lecture & Lab)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_pairs_query, ())
            ),
            ui.dropdown(
                name='ge_bio_1b',
                #label='For Science Majors and Minors only:',
                value=q.user.student_info['ge']['bio']['1b'] if (q.user.student_info['ge']['bio']['1b'] is not None) \
                    else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Science Majors and Minors)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (8,))
            ),
            #ui.separator(label='Select an additional science course:'),
            #nopre=True # check for easy classes by selecting those w/o prerequisites
            ui.dropdown(
                name='ge_bio_2',
                label='2. An additional course (3 credits)',
                value=q.user.student_info['ge']['bio']['2'] if (q.user.student_info['ge']['bio']['2'] is not None) \
                    else q.args.ge_bio_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
#                choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (10,))
                choices=await get_choices(timedConnection, ge_query, (10,))
            ),
        ]
    )
    return card

async def render_ge_comm_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    '''
    Create the General Education - Communications card
    '''
    timedConnection = q.user.conn
    if flex:
        box = location
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Communications', size=ui.TextSize.L),
                ui.checkbox(name='ge_comm_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_comm_1',
                label='1. WRTG 111 or equivalent (3 credits)',
                value=q.user.student_info['ge']['comm']['1'] if (q.user.student_info['ge']['comm']['1'] is not None) \
                    else q.args.ge_comm_1,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_2',
                label='2. WRTG 112 (3 credits)',
                value=q.user.student_info['ge']['comm']['2'] if (q.user.student_info['ge']['comm']['2'] is not None) \
                    else q.args.ge_comm_2,
                disabled=False,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_3',
                label='3. Another course (3 credits)',
                placeholder='(Select One)',
                value=q.user.student_info['ge']['comm']['3'] if (q.user.student_info['ge']['comm']['3'] is not None) \
                    else q.args.ge_comm_3,
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_4',
                label='4. Advanced writing course (3 credits)',
                placeholder='(Select One)',
                value=q.user.student_info['ge']['comm']['4'] if (q.user.student_info['ge']['comm']['4'] is not None) \
                    else q.args.ge_comm_4,
                trigger=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (4,))
            ),
        ]
    )
    return card

async def render_ge_math_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    '''
    Create the General Education - Mathematics card
    '''
    timedConnection = q.user.conn
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Mathematics', size=ui.TextSize.L),
                ui.checkbox(name='ge_math_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_math',
                label='One Course (3 credits)',
#                value=q.user.student_info['ge_math'] if (q.user.student_info['ge_math'] is not None) else q.args.ge_math,
                value=q.user.student_info['ge']['math'] if (q.user.student_info['ge']['math'] is not None) \
                    else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (5,))
            ),
        ]
    )
    return card

async def render_ge_research_card(q, menu_width, box='1 3 3 4', flex=False, location='grid'):
    '''
    Create the General Education - Research and Computing Literacy card
    '''
    timedConnection = q.user.conn
    if flex:
        box = location
    # make some defaults based on area of program chosen:
    if q.user.student_info['menu']['area_of_study'] == '1':
        q.user.student_info['ge']['res']['1'] = 'PACE 111B'
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Research and Computing Literacy', size=ui.TextSize.L),
                ui.checkbox(name='ge_res_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_res_1',
                label='1. Professional Exploration (3 credits)',
                value=q.user.student_info['ge']['res']['1'] if (q.user.student_info['ge']['res']['1'] is not None) \
                    else q.args.ge_res_1,
                # default value will depend on the major chosen
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (12,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills / Professional Development (1 credit)',
                value=q.user.student_info['ge']['res']['2'] if (q.user.student_info['ge']['res']['2'] is not None) \
                    else q.args.ge_res_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_query, (13,))
            ),
            ui.dropdown(
                name='ge_res_3',
                label='3. Computing or IT (3 credits)',
                value=q.user.student_info['ge']['res']['3'] if (q.user.student_info['ge']['res']['3'] is not None) \
                    else q.args.ge_res_3,
                trigger=True,
                required=True,
                placeholder='(Select 3-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (14,3))
            ),
           ui.dropdown(
                name='ge_res_3a',
                label='[or three 1-credit courses]:',
                required=True,
                value=q.user.student_info['ge']['res']['3a'] if (q.user.student_info['ge']['res']['3a'] is not None) \
                    else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                #label='Computing or Information Technology (1 credit)',
                value=q.user.student_info['ge']['res']['3b'] if (q.user.student_info['ge']['res']['3b'] is not None) \
                    else q.args.ge_res_3b,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                #label='Computing or Information Technology (1 credit each)',
                value=q.user.student_info['ge']['res']['3c'] if (q.user.student_info['ge']['res']['3c'] is not None) \
                    else q.args.ge_res_3c,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(timedConnection, ge_credits_query, (14,1))
            ),
        ]
    )
    return card

##############################################################
####################  GE PAGE (END)   ########################
##############################################################

###############################################################
####################  SCHEDULE PAGE (START) ###################
###############################################################

def d3plot(html, box='1 2 5 6', flex=False, location='horizontal', height='500px', width='100%'):
    if flex:
        box=ui.box(location, height=height, width=width)
    card = ui.frame_card(
        box=box,
        #title='Course Schedule',
        title='',
        content=html
    )
    return card

##############
async def render_schedule_menu(q, box='6 2 2 5', flex=False, location='middle_vertical', box_width='300px'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB)
    '''
    Sessions = ['Session 1', 'Session 2', 'Session 3']
    
    student_profile = q.user.student_info['student_profile']
    if student_profile == 'Full-time':
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 15
        default_courses_per_session = 3
    elif student_profile == 'Part-time':
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 9
        default_courses_per_session = 1
    else:
        # todo: enumerate the rest of the profile cases
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 2', 'Session 3']
        default_max_credits = 9
        default_courses_per_session = 1

    if flex:
        box = ui.box(location, width=box_width)
    card = ui.form_card(
        box=box,
        items=[
            ui.dropdown(
                name='first_term',
                label='First Term',
                value=q.user.student_info['first_term'] if (q.user.student_info['first_term'] is not None) \
                    else q.args.first_term,
                trigger=True,
                width='150px',
                # todo: create these choices via same function call as used in scheduling slots
                choices=[
                    ui.choice(name='spring2024', label="Spring 2024"),
                    ui.choice(name='summer2024', label="Summer 2024"),
                    ui.choice(name='fall2024', label="Fall 2024"),
                    ui.choice(name='winter2025', label="Winter 2025"),
                ]),
            #                ui.separator(),
            ui.checklist(
                name='checklist',
                label='Sessions Attending',
                choices=[ui.choice(name=x, label=x) for x in Sessions],
                values=default_sessions,  # set default
            ),
            ui.spinbox(
                name='courses_per_session',
                label='Courses per Session',
                width='150px',
                min=1, max=5, step=1, value=default_courses_per_session),
            #                ui.separator(label=''),
            ui.slider(name='slider', label='Max Credits per Term', min=1, max=18, step=1, 
                      value=default_max_credits),
            ui.inline(items=[
                ui.button(name='submit_schedule_menu', label='Submit', primary=True),
                ui.button(name='reset_schedule_menu', label='Reset', primary=False),
            ])
        ]
    )
    add_card(q, 'schedule_menu', card)

##############

async def render_schedule_page_table(q, df, box=None, location=None, width=None, height=None, flex=False):
    '''
    Input comes from 
    q:
    df:
    location:
    cardname:
    width:
    height:
    '''
    #df = q.user.student_info['df']['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', 
                        max_width='300', cell_overflow='wrap'),
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
        ui.table_column(name='term', label='Term', max_width='50', data_type='number'),        
        ui.table_column(name='session', label='Session', max_width='80', data_type='number'),        
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='change_time', label='Move Class'),
                    ui.command(name='lock_class', label='Lock Class'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
                str(row['term']),
                str(row['session']),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)

    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

###############################################################
####################  SCHEDULE PAGE (END)  ####################
###############################################################

#############################################################
####################  PROJECT PAGE (START) ##################
#############################################################

async def render_project_table(data, box='1 1 5 5', flex=False, location='middle_vertical', title='Project Status Table', height='520px'):

    if flex:
        box=location

    _project_table_columns = [
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
            #filterable=True,
            #searchable=True,
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
    _project_table_rows = [
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
        box=box,
        items=[
            ui.text(title, size=ui.TextSize.XL),
            ui.table(
                name='transactions',
                columns=_project_table_columns,
                rows=_project_table_rows,
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

#############################################################
####################  PROJECT PAGE (END)   ##################
#############################################################

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
