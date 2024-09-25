from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import (
    Any, 
    Dict, 
    Callable, 
    List, 
    Optional, 
    Union
)

import logging
import os
#from msal import ConfidentialClientApplication
import pandas as pd
import numpy as np

#import random
#import sqlite3

#import delete_me as delete

# 'templates' contains static html, markdown, and javascript D3 code
import templates
# cards contains static cards and python functions that render cards (render_... functions)
import cards

import frontend
from frontend import add_card, clear_cards
import backend
from backend import get_choices

# frontend contains functions for dealing with cards and the UI directly

# 'utils' contains all other python functions
import utils
#from utils import  get_choices_disable_all


######################################################
####################  Home page  #####################
######################################################



@on('#home/2')
async def home2(q: Q):
    clear_cards(q)

    #add_card(q, 'ai_enablement', return_ai_enablement_card(location='horizontal'))
    #await cards.render_interest_assessment_card(q, location='horizontal', width='33%')
    #await cards.render_personality_assessment_card(q, location='horizontal', width='33%')
    #cards.task2(q)
    #await cards.render_skills_assessment_card(q, location='top_horizontal', width='33%')

    card = frontend.create_program_selection_card(location='top_horizontal')
    add_card(q, 'program_selection_options', card)
    cards.tasks_checked1(q)

    await q.page.save()

@on('#home/3')
async def home3(q: Q):
    clear_cards(q)

    task_3_caption = f'''
### Task 3. Select Courses
#### Required courses:
- Your selected program includes required Major courses
- Selected General Education and Elective courses may also be required

### General Education and Elective courses:
- Select courses manually
  - Explore minors and use those courses to satisfy GE and Elective graduation requirements


### Task 4. Set a Schedule

'''

    task_4_caption = f'''
### Task 4. Set a Schedule

'''
    dark_theme_colors = '$red $pink $blue $azure $cyan $teal $mint $green $lime $yellow $amber $orange $tangerine'.split()

#    add_card(q, 'tasks', 
#        card = ui.wide_info_card(
#            box=ui.box('grid', width='400px'),
#            name='tasks',
#            icon='AccountActivity',
#            title='Tasks',
#            caption=task_list_caption
#        )
#    )

    add_card(q, 'task3', 
        card = ui.wide_info_card(
            box=ui.box('grid', width='400px'),
            name='task3',
            icon='AccountActivity',
            title='Tasks',
            caption=task_3_caption
        )
    )

    add_card(q, 'task4', 
        card = ui.wide_info_card(
            box=ui.box('grid', width='400px'),
            name='task4',
            icon='AccountActivity',
            title='Task 4',
            caption=task_4_caption
        )
    )

    # this will be an updated page
    #cards.render_welcome_back_card(q, box='horizontal')

#    add_card(q, 'philosophy', 
#        card = ui.wide_info_card(
#            box=ui.box('grid', width='400px'),
#            name='philosophy',
#            icon='LightningBolt',
#            title='First steps',
#            caption='''Welcome the student back. 
#
#Query about information.
#            '''
#    ))

    await cards.render_career_assessment_card(q, location='grid')

    #add_card(q, 'ai_enablement', cards.render_ai_enablement_card(location='grid'))
    #add_card(q, 'student_stub', cards.render_student_information_stub_card(location='grid'))
    #add_card(q, 'to_do_next', ui.markdown_card(
    #    box='grid',
    #    title='Next steps',
    #    content='Add links to continue, such as "Add Elective", "Update Schedule", etc.'
    #))

    #cards.render_registration_card(q)
    #cards.render_registration_card(q, width='40%', height=card_height, location='top_horizontal')

    #add_card(q, 'blank_card', 
    #    ui.form_card(
    #        box=ui.box('top_horizontal', width='60%', height=card_height),
    #        items=task_items
    #    )
    #)

    ## Show this card after entering 
    #add_card(q, 'demographics', 
    #    ui.form_card(
    #        box=ui.box('top_horizontal', width='30%'),
    #        items=[
    #            ui.text_xl('Tell us about yourself:'),
    #            ui.text('This information will help us to create your schedule'),
    #            ui.choice_group(name='attendance', label='I will be attending', choices=attendance_choices, required=True),
    #            ui.separator(label='', name='my_separator', width='100%', visible=True),
    #            ui.checkbox(name='financial_aid', label='I will be using Financial Aid'),
    #            ui.checkbox(name='transfer_credits', label='I have credits to transfer'),
    #            ui.button(name='submit', label='Submit', primary=True),
    #        ]
    #    )
    #)

    #await student_home(q)

    if q.app.debug:
        q.page['debug'] = await cards.return_debug_card(q)
    
    await q.page.save()

#############################
## Events on the Home page ##
#############################

@on()
async def next_demographic_1(q: Q) -> None:
    '''
    Respond to submission by clicking next on 'Tell us about yourself' card 1
    (from demographics1 function)
    '''
    # need to map these to the right place, this is a placeholder for now
    q.client.my_dict = {
        'attendance': q.args.attendance,
        'financial_aid': q.args.financial_aid,
        'transfer_credits': q.args.transfer_credits
    }

    logging.info('Redirecting to the #home/1 page')
    q.page['meta'].redirect = '#home/1'
    await q.page.save()

@on()
async def next_demographic_2(q: Q) -> None:
    '''
    Respond to submission by clicking next on 'Tell us about yourself' card 1
    (from demographics1 function)
    '''
    # need to map these to the right place, this is a placeholder for now
    q.client.my_dict2 = {'resident_status': q.args.resident_status}

    logging.info('Redirecting to the #home/2 page')
    q.page['meta'].redirect = '#home/2'
    await q.page.save()


#########################################################
####################  Program pages  ####################
#########################################################

#############################################
###  Program page: Dropdown Menu Actions  ###
#############################################

def dropdown_debug(q):
    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.client.student_info values:
{q.client.student_info}

### q.client values:
{q.client}
'''
    return content


########################################################
####################  Skills pages  ####################
########################################################

@on('#skills')
async def skills(q: Q):
    clear_cards(q) # will use in the individual functions

    timed_connection = q.client.conn
    card = await frontend.return_skills_menu(timed_connection, location='horizontal', width='300px')
    add_card(q, 'skill_card', card)

    await q.page.save()


########################################################
####################  Course pages  ####################
########################################################

async def admin_course(q: Q):
    await student_course(q)

async def coach_course(q: Q):
    await student_course(q)

async def student_course(q: Q):
    if q.client.student_data['schedule'] is not None:
        add_card(q, 'courses_instructions', ui.form_card(
            box='top_horizontal',
            items=[
                ui.text('**Instructions**: You have selected courses. You may now add electives or view your schedule.')
            ]
        ))
        await cards.render_course_page_table_use(q, location='horizontal')

    await q.page.save()

@on('#course')
async def course(q: Q):
    clear_cards(q)

    if q.client.role == 'admin':
        # admin course page
        await admin_course(q)

    elif q.client.role == 'coach':
        # coach course page
        await coach_course(q)
        
    elif q.client.role == 'student':
        # student course page
        await student_course(q)
        
    else:
        pass
        
    if q.app.debug_course:
        add_card(q, 'course_debug', await cards.return_debug_card(q))

    await q.page.save()

###################################################################
####################  General Education pages  ####################
###################################################################

async def admin_ge(q: Q):
    await student_ge(q)

async def coach_ge(q: Q):
    await student_ge(q)

async def student_ge(q: Q):
    clear_cards(q)

    add_card(q, 'welcome_ge', ui.form_card(
        box=ui.box('top_horizontal', width='100%'),
        items=[
            ui.text_l('Select your General Education courses here.'),
            #ui.text('We will guide you through this experience.')
        ]
    ))
    menu_width = '300px'
    location = 'grid'
    width = '330px'
    await cards.render_ge_comm_card(q, cardname='ge_comm', location=location, width=width)
    await cards.render_ge_res_card(q, cardname='ge_res', location=location, width=width)
    await cards.render_ge_bio_card(q, cardname='ge_bio', location=location, width=width)
    await cards.render_ge_math_card(q, cardname='ge_math', location=location, width=width)
    await cards.render_ge_arts_card(q, cardname='ge_arts', location=location, width=width)
    await cards.render_ge_beh_card(q, cardname='ge_beh', location=location, width=width)



###############
## GE Events ##
###############

def ge_debug_content(q):
    result = f'''
### q.client.student_info['ge'] values:

- Arts: {q.client.student_info['ge']['arts']}
- Beh: {q.client.student_info['ge']['beh']}
- Bio: {q.client.student_info['ge']['bio']}
- Comm: {q.client.student_info['ge']['comm']}
- Math: {q.client.student_info['ge']['math']}
- Res: {q.client.student_info['ge']['res']}

### q.args values:
{q.args}

### q.events values:
{q.events}

#### q.page['ge_bio']
{dir(q.page['ge_bio'])}

{ q.page['ge_bio'].items['ge_bio_1a'].value }

#### Whole GE
{q.client.student_info['ge']}

### q.client value:
{q.client}
'''
    return result


##########################################
## GE set variables from pulldown menus ##
##########################################

# (Worry about making this efficient later)







##########################################################
####################  Schedule pages  ####################
##########################################################


@on('#schedule')


### Table Menu Items
#@on()
#async def schedule_table.click(q: Q):
#    pass

###########################
## Schedule Menu actions ##
###########################

@on()
async def submit_schedule_menu(q: Q):
    '''
    Respond to Submit button on menu on Schedule page
    Launch generate_periods(start_term='SPRING 2024', years=8, max_courses=3, max_credits=18, 
                     summer=False, sessions=[1,3], as_df=True):
    '''
    schedule_menu = {}
    schedule_menu['first_term'] = q.args.first_term
    schedule_menu['sessions'] = q.args.sessions_checklist
    schedule_menu['max_courses'] = q.args.courses_per_session
    schedule_menu['max_credits'] = q.args.max_credits
    schedule_menu['attend_summer'] = q.args.attend_summer
    q.client.student_info['schedule_menu'] = schedule_menu

    q.client.student_data['periods'] = utils.generate_periods(
            start_term=schedule_menu['first_term'],
            max_courses=schedule_menu['max_courses'],
            max_credits=schedule_menu['max_credits'],
            summer=schedule_menu['attend_summer'],
            sessions=schedule_menu['sessions'],
            as_df=True
        )
    

    q.page['schedule_debug'].content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.client.student_info values:
{q.client.student_info}

### q.client.student_info['schedule_menu'] values:
{q.client.student_info['schedule_menu']}

### q.client.student_data values:

#### Required:
{q.client.student_data['required']}

#### Periods:
{q.client.student_data['periods']}

#### Schedule:
{q.client.student_data['schedule']}
    '''
    await q.page.save()


############################
## Schedule Table actions ##
############################

@on()
async def schedule_table(q: Q):
    '''
    Respond to events (clicking Course link or double-clicking row)
    in the table on Schedule page. This will display the course description
    by default.

    Notes:
      - q.args.table_name is set to [row_name]
      - the name of the table is 'schedule_table'
      - the name of the row is name = row['name']    
    '''
    coursename = q.args.schedule_table[0] # am I getting coursename wrong here?
    frontend.course_description_dialog(q, coursename, which='schedule')
    logging.info('The value of coursename in schedule_table is ' + coursename)
    await q.page.save()

# view description
@on()
async def view_schedule_description(q: Q):
    '''
    Respond to the menu event 'Course Description'
    (Calls same function as schedule_table above)
    '''
    coursename = q.args.view_schedule_description
    frontend.course_description_dialog(q, coursename, which='schedule')
    logging.info('The value of coursename in view_schedule_description is ' + str(coursename))
    await q.page.save()

# move class
@on()
async def move_class(q: Q):
    pass

# lock class
@on()
async def lock_class(q: Q):
    pass

# select elective (may be multiple tables)
@on()
async def select_elective(q: Q):
    pass

#####################################################
####################  End pages  ####################
#####################################################


## below is a dummy function for demonstration
@on()
async def show_dialog(q: Q):
    # Create a dialog with a close button
    delete.example_dialog(q)
    await q.page.save()
