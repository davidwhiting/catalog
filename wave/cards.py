from h2o_wave import ui, copy_expando, expando_to_dict
from typing import Optional, List
import pandas as pd
import numpy as np

import utils
from utils import add_card, clear_cards
from utils import get_query, get_query_one, get_query_dict, get_query_df
#from utils import get_choices, get_choices_with_disabled, get_role, \
#    get_ge_choices, get_catalog_program_sequence, get_student_progress_d3
#from utils import generate_periods, update_periods, generate_schedule, handle_prerequisites, \
#    schedule_courses_old, update_courses, move_courses_forward
#import sys

######################################################################
##################  TEST FUNCTIONS TO BE DELETED  ####################
######################################################################


######################################################################
##################  DEFINITIONS AND QUERIES  #########################
######################################################################

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

### These queries are used in app.py for menus and  ###
### render_dropdown_menus_horizontal                ###

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

######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

########################################################
####################  LAYOUT CARDS  ####################
########################################################

def render_meta_card(flex=True):
    title='UMGC Wave App'
    theme_name='UMGC'
    content_zones = [
        # Specify various zones and use the one that is currently needed. Empty zones are ignored.
        # Usually will not need the top_ or bottom_ versions
        ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
        ui.zone('top_vertical'),
        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
        ui.zone('vertical'),
        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'),
        ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
        ui.zone('bottom_vertical'),
        ui.zone('debug', direction=ui.ZoneDirection.ROW)
    ]
    UMGC_themes=[ui.theme( # UMGC red: '#a30606', UMGC yellow: '#fdbf38'
        name='UMGC',
        primary='#a30606', 
        text='#000000',
        card='#ffffff',
        page='#e2e2e2', 
    )]
    UMGC_layouts=[ui.layout(
        breakpoint='xs', 
        #min_height='100vh', 
        zones=[
            # size='0' keeps zone from expanding
            ui.zone('header', size='80px'), 
            ui.zone('content', zones=content_zones, size='100%-80px'),
            ui.zone('footer', size='0'),
        ]
    )]
    card = ui.meta_card(
        box = '',
        themes = UMGC_themes,
        theme = theme_name,
        title = title,
        layouts = UMGC_layouts if flex else None
    )
    return card 

def render_header_card(q, box='1 1 7 1'):
    '''
    flex: Use the old flex layout system rather than the grid system
          (flex was not working correctly, can debug later)
    Create separate tabs for different roles: guest, student, coach, admin
    '''
    flex = q.app.flex
    guest_tab_items = [
        ui.tab(name='#login',    label='Login'),
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]
    student_tab_items = [
        ui.tab(name='#login',    label='Login'),
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]
    coach_tab_items = [
        ui.tab(name='#login',    label='Login'),
        ui.tab(name='#admin',    label='Coach'),
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]
    admin_tab_items = [
        ui.tab(name='#login',    label='Login'),
        ui.tab(name='#admin',    label='Admin'),
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]

    if q.user.role == 'admin':
        tab_items = admin_tab_items
        textbox_label = 'Admin Name'
        textbox_value = q.user.name
    elif q.user.role == 'coach':
        tab_items = coach_tab_items
        textbox_label = 'Coach Name'
        textbox_value = q.user.name
    elif q.user.role == 'student':
        tab_items = student_tab_items
        textbox_label = 'Student Name'
        textbox_value = q.user.name
    else:
        tab_items = guest_tab_items
        textbox_label = 'Guest'
        textbox_value = '[Login button here]'

    older_tab_items = [
        ui.tab(name='#home', label='Home'),
        #ui.tab(name='#student', label='Student Info'),
        ui.tab(name='#major', label='Program'), # 'Select Program'
        ui.tab(name='#course', label='Course'), # 'Select Courses'
        #ui.tab(name='#ge', label='GE'), 
        #ui.tab(name='#electives', label='Electives'), # 'Select Courses'
        ui.tab(name='#schedule', label='Schedule'), # 'Set Schedule'
        #ui.tab(name='#project', label='Status'), # 'Project Plan'
    ]
    if flex:
        box='header'
    card = ui.header_card(
        box=box, 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(
                name='tabs', 
                value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, 
                items=tab_items,
            ),
        ],
        items=[
            ui.textbox(
                name='textbox_default', 
                label=textbox_label,
                value=textbox_value, 
                disabled=True
            )
        ]
    )
    return card

def render_login_header_card(q, box='1 1 7 1'):
    '''
    flex: Use the old flex layout system rather than the grid system
          (flex was not working correctly, can debug later)
    Create separate tabs for different roles: guest, student, coach, admin
    '''
    flex = q.app.flex

    login_tab_items = [
        ui.tab(name='#login',     label='Login'),
    ]
    tab_items = login_tab_items

    if flex:
        box='header'
    card = ui.header_card(
        box=box, 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(
                name='tabs', 
                value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, 
                items=tab_items,
            ),
        ],
        #items=[
        #    ui.textbox(
        #        name='textbox_default', 
        #        label='',
        #        value='',
        #        disabled=True
        #    )
        #]
    )
    return card

def render_footer_card(box='1 10 7 1', flex=True):
    '''
    flex: Use the flex layout system rather than the grid system
    '''

    if flex:
        box='footer'
    card = ui.footer_card(
        box=box,
        caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
        '''
    )
    return card

#######################################################
####################  DEBUG CARDS  ####################
#######################################################

async def render_debug_card(q, box='3 3 1 1', location='debug', width='100%', height='300px'):
    '''
    Show q.client information in a card for debugging
    '''
    expando_dict = expando_to_dict(q.user)
    q_user_filtered = {k: v for k, v in expando_dict.items() if k not in ['student_info', 'student_data']}

    #### q.user.student_data values:
    #{q.user.student_data}
    flex = q.app.flex


    if flex:
        box = ui.box(location, width=width, height=height)

    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.user.student_info values:
{q.user.student_info}

### q.user.student_data values:

#### Required:
{q.user.student_data['required']}

#### Schedule:
{q.user.student_data['schedule']}

### remaining q.user values:
{q_user_filtered}

### q.user values

### q.app values:
{q.app}

    '''
    card = ui.markdown_card(
        box,
        title='Debug Information', 
        content=content 
    )
    return card

###############################################################
####################  LOGIN PAGE  #############################
###############################################################


async def render_user_dropdown(q, box=None, location='horizontal', menu_width='300px'):
    '''
    Function to create a dropdown menu of sample users to demo the wave app
    '''
    timedConnection = q.user.conn
    flex = q.app.flex
    if flex:
        box = location

    query = '''
        SELECT a.id AS name, 
            trim(a.firstname || ' ' || a.lastname || ' (' || b.role || ')') AS label
        FROM users a, roles b
        WHERE a.role_id = b.id
    '''
    #choices=await utils.get_choices(timedConnection, query)

    choicesdict = [
        {'name': 1, 'label': 'Admin (admin role)'},
        {'name': 2, 'label': 'Coach (coach role)'},
        {'name': 3, 'label': 'John Doe (full-time student with program selected)'},
        {'name': 4, 'label': 'Jane Doe (part-time transfer student with program selected)'},
        {'name': 5, 'label': 'Jim Doe (new student)'},
        {'name': 6, 'label': 'Tom Doe (military student, no program selected)'},
    ]

    choices = [ui.choice(str(row['name']), row['label']) for row in choicesdict]

    choicegroup = ui.choice_group(
        name='choice_group', 
        label='Pick one', 
        required=True, 
        choices=choices
    )
    button = ui.button(name='select_sample_user', label='Submit', primary=True)

    dropdown = ui.dropdown(
        name='sample_user',
        label='Sample User',
        value=q.args.sample_user,
        trigger=True,
        placeholder='(Select)',
        width=menu_width,
        choices=choices
    )
    card = ui.form_card(box=box,
        items=[
            ui.text_xl('Example users'),
            choicegroup,
            #dropdown, 
            button
        ]
    ) 
    return card


##############################################################
####################  HOME PAGE  #############################
##############################################################

def render_welcome_back_card(q, location='vertical', box='1 3 3 3', title=''):
    student_info = q.user.student_info
    flex = q.app.flex

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
    #)]))


def render_welcome_card_old(q, location='top_vertical', width='400px', box='1 2 7 1'):
    flex = q.app.flex
    if flex:
        box = ui.box(location, width=width)

    add_card(q, 'welcome_home', ui.form_card(
        box=box,
        items=[
            ui.text_l('Welcome to the UMGC Registration Assistant'),
            ui.text('(The Home page will collect student information)')
        ]
    ))

def render_ai_enablement_card(box='1 1 2 2', location='grid', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
    card = ui.wide_info_card(
        box=box,
        name='ai',
        icon='LightningBolt',
        title='AI Enablement',
        caption='*Interest* or *Skills* assessments critical for AI recommendations.'
    )
    return card

def render_career_assessment_card(box='1 1 2 2', location='horizontal', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
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

def render_student_information_stub_card(box='1 1 2 2', location='horizontal', width='400px', flex=True):
    if flex:
        box=ui.box(location, width=width)
    caption=f'Gather incomplete student information. Walk students through transfer credits. Access allowable data from UMGC servers.'
    card = ui.wide_info_card(
        box=box,
        name='StudentAssessments',
        icon='AccountActivity',
        title='Guided Student Updates',
        caption=caption
    )
    return card

##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################

async def render_dropdown_menus_horizontal(q, box='1 2 7 1', location='horizontal', 
                                           menu_width='300px'):
    '''
    Create menus for selecting degree, area of study, and program
    '''
    flex = q.app.flex
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

    current_disabled = q.app.disabled_program_menu_items
    
    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(q.user.student_info['menu']['degree']) if \
                (q.user.student_info['menu']['degree'] is not None) else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices=await utils.get_choices(timedConnection, degree_query)
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
                await utils.get_choices(timedConnection, area_query, (q.user.student_info['menu']['degree'],))
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
                await utils.get_choices(
                    timedConnection, 
                    program_query, 
                    (q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study']),
                    disabled = current_disabled
                )
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
        
    return add_card(q, 'dropdown', card)

    ########################

async def render_program_description(q, box='1 3 7 2', location='top_vertical', width='100%', height='100px'):
    '''
    Renders the program description in an article card
    :param q: instance of Q for wave query
    :param location: page location to display
    '''
    flex = q.app.flex
    timedConnection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    if flex:
        box = ui.box(location, width=width, height=height)

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

async def render_program_dashboard(q, box=None, location='horizontal', width='100px'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    flex = q.app.flex
    timedConnection = q.user.conn
    title = q.user.student_info['degree_program'] # program name

    if flex:
        box = ui.box(location, width=width)
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

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

async def render_program_table(q, box='1 5 6 5', location='horizontal', width='90%', 
                               height='500px', check=True, ge=False, elective=False):
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
    flex = q.app.flex
    df = q.user.student_data['required']

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
        no_rows = ((df['type'].str.upper() == record_type).sum() == 0)

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
        df, collapsed=False, check=False
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
                    ui.command(name='view_program_description', label='Course Description'),
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

async def render_program(q):
    await render_program_description(q, location='top_vertical', height='250px', width='100%')
    await render_program_table(q, location='horizontal', width='90%')
    await render_program_dashboard(q, location='horizontal', width='150px')


##############################################################
####################  COURSES PAGE  ##########################
##############################################################

def render_courses_header(q, box='1 2 7 1', location='horizontal'):
    flex = q.app.flex
    degree_program = q.user.student_info['degree_program']
    if flex:
        box = ui.box(location)
    content=f'**Program Selected**: {degree_program}'
    add_card(q, 'courses_header', ui.form_card(
        box=box,
        items=[
            ui.text_l(content),
            #ui.text('We will guide you through this experience.')
        ]
    ))

async def render_course_page_table_use(q, box=None, location=None, width=None, height=None, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    data: a list of dictionaries, each element corresponding to a row of the table 
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    df = q.user.student_data['schedule']

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

async def render_course_page_table(q, df, box=None, location=None, width=None, height=None, 
                                   check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    df: a Pandas df containing the table
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
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

#######################################################
####################  GE PAGE  ########################
#######################################################


########################################################
####################  SCHEDULE PAGE  ###################
########################################################

async def render_d3plot(q, html, box='1 2 5 6', location='horizontal', 
        height='500px', width='100%'):
    '''
    Create the D3 display from html input
    '''
    flex = q.app.flex
    if flex:
        box=ui.box(location, height=height, width=width)
    card = ui.frame_card(
        box=box,
        #title='Course Schedule',
        title='',
        content=html
    )
    #return card
    add_card(q, 'd3_display', card)

async def render_schedule_menu(q, box='6 2 2 5', location='vertical', 
                               width='300px'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.user.student_info fields)
    '''
    flex = q.app.flex

    Sessions = ['Session 1', 'Session 2', 'Session 3']
    default_attend_summer = True
    student_profile = q.user.student_info['student_profile']
    if student_profile == 'Full-time':
        ## full-time: 
        ##   - 14 week and 17 week terms: (min 12, max 18)
        ##   - 4 week term: (min 3, max 6)
        ## half-time:
        ##   - 14 week and 17 week terms: (min 6)

        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 18
        default_courses_per_session = 3
    elif student_profile == 'Part-time':
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 7
        default_courses_per_session = 1
    else:
        # todo: enumerate the rest of the profile cases
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 13
        default_courses_per_session = 2

    if flex:
        box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.dropdown(
                name='first_term',
                label='First Term',
                value=q.user.student_info['first_term'] if (q.user.student_info['first_term'] is not None) \
                    else q.args.first_term,
                trigger=False,
                width='150px',
                # todo: create these choices via same function call as used in scheduling slots
                choices=[
                    ui.choice(name='Spring 2024', label="Spring 2024"),
                    ui.choice(name='Summer 2024', label="Summer 2024"),
                    ui.choice(name='Fall 2024', label="Fall 2024"),
                    ui.choice(name='Winter 2025', label="Winter 2025"),
                ]),
            #                ui.separator(),
            ui.checklist(
                name='sessions_checklist',
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
            ui.slider(name='max_credits', label='Max Credits per Term', min=1, max=18, 
                step=1, value=default_max_credits),
            ui.checkbox(name='attend_summer', label='Attending Summer', 
                value=default_attend_summer),
            ui.inline(items=[
                ui.button(name='submit_schedule_menu', label='Submit', primary=True),
                ui.button(name='reset_schedule_menu', label='Reset', primary=False),
            ])
            #ui.button(name='submit_schedule_menu', label='Submit', primary=True),
        ]
    )
    add_card(q, 'schedule_menu', card)

async def render_schedule_page_table(q, box=None, location='horizontal', width='90%', height=None):
    '''
    Input comes from 
    q:
    location:
    cardname:
    width:
    height:
    '''
    flex = q.app.flex
    df = q.user.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_schedule_description', label='Course Description'),
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
        ui.table_column(name='locked', label='Locked', max_width='50', data_type='number'),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_schedule_description', label='Course Description'),
                    ui.command(name='move_class', label='Move Class'),
                    ui.command(name='lock_class', label='Lock/Unlock Class'),
                ]
        ))
        #            ui.command(name='select_elective', label='Select Elective'),
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
                str(row['locked']),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        #box = ui.box(location, height=height, width=width)
        box = ui.box(location, width=width)

    degree_program = q.user.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'schedule_table', ui.form_card(
        box=box,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='schedule_table',
                downloadable=True,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card


######################################################
####################  PROJECT PAGE  ##################
######################################################

