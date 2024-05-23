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

##############################################################
####################  DEBUG CARDS (START) ####################
##############################################################

def render_debug(q, location='debug', width='25%', height='230px'):
    add_card(q, 'debug_user_info', render_debug_user_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_info', render_debug_card(q, location=location, width=width, height=height)) 

##############################################################
####################  HOME PAGE  #############################
##############################################################

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

##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################


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

async def render_program_coursework_table(q, box='1 3 5 7', location='middle_vertical', width='100%', height='500px', flex=False):
    '''
    Create program coursework requirement table
    '''
    df = await utils.get_required_program_courses(q, q.user.student_info['program_id'])
    q.user.student_data['required'] = df


    await _render_program_table(q, box=box, location=location, width=width, height=height)

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


##############

##############

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
