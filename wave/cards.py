from h2o_wave import ui
from typing import Optional, List

import utils
#from utils import add_card, clear_cards
#from utils import get_query, get_query_one, get_query_dict, get_query_df
#from utils import get_choices, get_choices_with_disabled, get_role, \
#    get_ge_choices, get_catalog_program_sequence, get_student_progress_d3
#from utils import generate_periods, update_periods, generate_schedule, handle_prerequisites, \
#    schedule_courses_old, update_courses, move_courses_forward
#import pandas as pd
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




##############################################################
####################  HOME PAGE  #############################
##############################################################


##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################


##############################################################
####################  COURSES PAGE  ##########################
##############################################################


#######################################################
####################  GE PAGE  ########################
#######################################################


########################################################
####################  SCHEDULE PAGE  ###################
########################################################


######################################################
####################  PROJECT PAGE  ##################
######################################################

