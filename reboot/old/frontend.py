
from contextlib import asynccontextmanager
from h2o_wave import Q, ui
from typing import Any, Dict, Callable, List, Optional, Union
#import asyncio
#import logging
import numpy as np
import pandas as pd
#import sqlite3
#import time
#import warnings
import backend


#######################################################
####################  Q FUNCTIONS  ####################
#######################################################

########################################################
####################  MENU QUERIES  ####################
########################################################

### These queries are used in app.py for menus and  ###
### render_dropdown_menus_horizontal                ###

degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
area_query = '''
    SELECT DISTINCT menu_area_id AS name, area_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ?
'''
program_query_old = '''
    SELECT program_id AS name, program_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''
program_query = '''
    SELECT program_id AS name, program_name AS label, disabled
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''
########################################################
####################  LAYOUT CARDS  ####################
########################################################

def return_header_card(q: Q) -> ui.header_card:
    '''
    Returns a header card with tabs for different roles: student, coach, admin
    Called in app.py.
    '''
    student_tab_items = [
        ui.tab(name='#login',     label='[Login]'),
        ui.tab(name='#home',      label='Home'),
        ui.tab(name='#skills',    label='Skills'),
        ui.tab(name='#program',   label='Program'),
        ui.tab(name='#course',    label='Courses'),
        ui.tab(name='#ge',        label='GE'), 
        ui.tab(name='#electives', label='Electives'), # 'Select Courses'
        ui.tab(name='#schedule',  label='Schedule')
    ]

    q.user.role = 'student'
    tab_items = student_tab_items
    textbox_label = 'Name'
    #textbox_value = q.user.name
    textbox_value = "John Doe"

    # Determine the current page
    current_page = q.args['#'] if '#' in q.args else 'home'

    box='header'
    card = ui.header_card(
        box=box, 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(
                name='tabs', 
                value=f'#{current_page}',
                link=True, 
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

def return_login_header_card(q: Q) -> ui.header_card:
    '''
    Create a header card with a login tab.
    '''

    login_tab_items = [
        ui.tab(name='#login',     label='Login'),
    ]
    tab_items = login_tab_items

    card = ui.header_card(
        box='header', 
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
    )
    return card

def return_footer_card() -> ui.footer_card:
    '''
    Footer card with caption for entire app.
    Called in app.py.
    '''
    card = ui.footer_card(
        box='footer',
        caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
        '''
    )
    return card

##########################################################
####################  HOME PAGE ##########################
##########################################################
def create_program_selection_card(location='horizontal', width='60%'):
    """
    Create the program selection card
    """
    card = ui.form_card(
        box=ui.box(location, width=width),
        #name='program_selection',
        #title='Select a UMGC Program',
        #caption='Choose an option to explore UMGC programs',
        #category='Program Selection',
        #icon='Education',
        items=[
            ui.text_xl(content='**Select a UMGC Program**'),
            ui.link(label='Option 1: Explore programs on your own', path='/#program'),
            ui.link(label='Option 2: Select a program based on your skills', path='/#skills'),
            ui.link(label='Option 3: Select a program based on your interests', disabled=True),
            ui.link(label='Option 4: Select a program that finished your degree the quickest', disabled=True)
        ]
    )
    return card


##############################################################
####################  PROGRAMS PAGE ##########################
##############################################################

async def render_dropdown_menus_horizontal(q, location='horizontal', menu_width='300px'):
    '''
    Create menus for selecting degree, area of study, and program
    '''

    timed_connection = q.user.conn    
    enabled_degree = {"Bachelor's", "Undergraduate Certificate"}
    disabled_programs = q.app.disabled_program_menu_items

    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(q.user.student_info['menu']['degree']) if \
                (q.user.student_info['menu']['degree'] is not None) else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices = await backend.get_choices(timed_connection, degree_query, disabled=None, enabled=enabled_degree)
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
                await backend.get_choices(timed_connection, area_query, 
                                          params=(q.user.student_info['menu']['degree'],))
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
                await backend.get_choices(timed_connection, program_query, 
                    params=(q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study']),
                    disabled=disabled_programs
                )
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='select_program', label='Select Program'),
            #ui.command(name='classes_menu', label='Classes', 
            #    items=[
            #        ui.command(name='add_ge', label='Add GE'),
            #        ui.command(name='add_elective', label='Add Electives'),  
            #]),
            ui.command(name='add_ge', label='Add GE'),
            ui.command(name='add_elective', label='Add Electives')  
    ])

    card = ui.form_card(
        box = location,
        items = [
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
        
    add_card(q, 'dropdown', card)

    ########################

############################################################
####################  SKILLS PAGE ##########################
############################################################

async def return_skills_menu(timed_connection, location='vertical', width='300px', inline=False):
    '''
    Create skills choice menu
    Will send the selected skills to the database query and return a list of courses

    '''
    #timed_connection = q.user.conn
    skills_query = 'SELECT id AS name, name AS label, explanation AS tooltip FROM Skills'
    choices = await backend.get_choices_new(timed_connection, skills_query, disabled={""}, tooltip=False)

    card = ui.form_card(
        box = ui.box(location, width=width),
        items=[
            #                ui.separator(),
            ui.checklist(
                name='skills_checklist',
                label='Skills',
                inline=inline,
                choices = choices,
            ),
            #ui.number(name='result_limit', label='Number of results', min=5, max=15, step=1, value=7),
            #ui.inline(items=[
            ui.button(name='submit_skills_menu', label='Submit', primary=True),
            ui.button(name='reset_skills_menu', label='Reset', primary=False),
            #])
        ]
    )
    return card

async def return_skills_table(results, location='horizontal'):
    """
    Return the skills table given input of results from get_query_dict
    Called by submit_skills_menu
    """
    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='program', label='Program', searchable=False, min_width='250'),
        ui.table_column(name='score', label='Score', searchable=False, min_width='100'), 
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='explore_skills_program', label='Explore Program'),
                    ui.command(name='select_skills_program', label='Select Program'),
                ]
        ))
    ]
    rows = [
        ui.table_row(
            name=str(row['id']),
            #name=row['program'],
            cells=[
                #str(row['seq']),
                row['program'],
                #str(row['TotalScore']),
                f"{row['TotalScore']:.3f}"
            ]
        ) for row in results
    ]
    card = ui.form_card(
        box=location,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='program_skills_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                columns=columns,
                rows=rows
            )
        ]
    )
    return card


######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################


def course_description_dialog(q, course, which='schedule'):
    '''
    Create a dialog for the course description for a table.
    This will be used for multiple tables on multiple pages.
    course: indicate what course it's for
    df: DataFrame that the table was created from

    to do: course in the schedule df is called 'name'
           course is called course in the required df
           should simplify by changing schedule df to course AFTER
           updating d3 javascript code, since it's expecting name
    '''
    if which in ['required', 'schedule']:
        #df = q.user.student_data[which]
        if which == 'schedule':
            df = q.user.student_data['schedule']
            description = df.loc[df['name'] == course, 'description'].iloc[0]
   
        elif which == 'required':
            df = q.user.student_data['required']
            description = df.loc[df['course'] == course, 'description'].iloc[0]

        #description = df.loc[df['course'] == course, 'description'].iloc[0]

        q.page['meta'].dialog = ui.dialog(
            name = which + '_description_dialog',
            title = course + ' Course Description',
            width = '480px',
            items = [ui.text(description)],
            # Enable a close button
            closable = True,
            # Get notified when the dialog is dismissed.
            events = ['dismissed']
        )
    else:
        pass

