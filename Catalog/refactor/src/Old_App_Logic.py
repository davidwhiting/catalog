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


#####################################################
####################  End pages  ####################
#####################################################


## below is a dummy function for demonstration
@on()
async def show_dialog(q: Q):
    # Create a dialog with a close button
    delete.example_dialog(q)
    await q.page.save()
