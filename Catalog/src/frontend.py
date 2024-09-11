
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

######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name: str, card) -> None:
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
            choices = await backend.get_choices(timed_connection, degree_query, enabled=enabled_degree)
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
            ui.command(name='program', label='Save Program'),
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

