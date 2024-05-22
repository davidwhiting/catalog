from h2o_wave import ui, copy_expando, expando_to_dict
from typing import Optional, List
import pandas as pd
import numpy as np

import utils
from utils import add_card, clear_cards
#from utils import get_query, get_query_one, get_query_dict, get_query_df
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

def render_header_card(q, box='1 1 7 1', flex=True):
    '''
    flex: Use the old flex layout system rather than the grid system
          (flex was not working correctly, can debug later)
    Create separate tabs for different roles: guest, student, coach, admin
    '''
    guest_tab_items = [
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]
    student_tab_items = [
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]
    coach_tab_items = [
        ui.tab(name='#admin',    label='Coach'),
        ui.tab(name='#home',     label='Home'),
        ui.tab(name='#program',  label='Program'),
        ui.tab(name='#course',   label='Course'),
        ui.tab(name='#schedule', label='Schedule'),
    ]
    admin_tab_items = [
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

#ui.dropdown(
#    name='user_dropdown',
#    label='Name',
#    value=str(q.user.user_id) if (q.user.user_id is not None) else q.args.user_dropdown,
#    trigger=True,
#    width='200px',
#    #choices=await get_choices(q, user_query)
#    choices = [
#        ui.choice(name=str(0), label='Guest'),
#        ui.choice(name=str(1), label='Admin'),
#        ui.choice(name=str(2), label='Counselor'),
#        ui.choice(name=str(3), label='John Doe'),
#        ui.choice(name=str(4), label='Jane Doe'),
#        ui.choice(name=str(5), label='Jim Doe'),
#        ui.choice(name=str(6), label='Sgt Doe'),
#    ]
#)


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

async def render_debug_card(q, box='3 3 1 1', flex=True, location='debug', width='100%', height='300px'):
    '''
    Show q.client information in a card for debugging
    '''
    expando_dict = expando_to_dict(q.user)
    q_user_filtered = {k: v for k, v in expando_dict.items() if k not in ['student_info', 'student_data']}

    #### q.user.student_data values:
    #{q.user.student_data}

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


##############################################################
####################  HOME PAGE  #############################
##############################################################


##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################

async def render_dropdown_menus_horizontal(q, box='1 2 7 1', location='horizontal', flex=True, 
                                           menu_width='300px'):
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
        
    return card

    ########################


##############################################################
####################  COURSES PAGE  ##########################
##############################################################

async def render_course_page_table(q, df, box=None, location=None, width=None, height=None, 
                                   flex=True, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    df: a Pandas df containing the table
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

async def render_d3plot(q, html, box='1 2 5 6', flex=True, location='horizontal', 
        height='500px', width='100%'):
    '''
    Create the D3 display from html input
    '''
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

async def render_schedule_menu(q, box='6 2 2 5', flex=True, location='vertical', 
                               width='300px'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.user.student_info fields)
    '''
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
                    ui.choice(name='spring2024', label="Spring 2024"),
                    ui.choice(name='summer2024', label="Summer 2024"),
                    ui.choice(name='fall2024', label="Fall 2024"),
                    ui.choice(name='winter2025', label="Winter 2025"),
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
            ui.slider(name='max_credit_slider', label='Max Credits per Term', min=1, max=18, 
                step=1, value=default_max_credits),
            ui.checkbox(name='attend_summer', label='Attending Summer', 
                value=default_attend_summer),
            ui.inline(items=[
                ui.button(name='submit_schedule_menu', label='Submit', primary=True),
                #ui.button(name='reset_schedule_menu', label='Reset', primary=False),
            ])
            #ui.button(name='submit_schedule_menu', label='Submit', primary=True),
        ]
    )
    add_card(q, 'schedule_menu', card)

async def render_schedule_page_table(q, box=None, location='horizontal', width='90%', height=None, 
                                    flex=True):
    '''
    Input comes from 
    q:
    location:
    cardname:
    width:
    height:
    '''
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
                    ui.command(name='lock_class', label='Lock Class'),
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

