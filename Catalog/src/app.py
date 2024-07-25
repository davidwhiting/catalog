from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import logging
import os
#from msal import ConfidentialClientApplication
import requests
import pandas as pd
import numpy as np

#import random
#import sqlite3

#import delete_me as delete

# 'templates' contains static html, markdown, and javascript D3 code
import templates
# cards contains static cards and python functions that render cards (render_... functions)
import cards
# 'utils' contains all other python functions
import utils
from utils import add_card, clear_cards, get_choices, get_choices_disable_all

##########################################
#############  Update Notes ##############
##########################################

# This is a simplified version for demos
# There is still a lot of work that needs to be done
# Tasks:
#   - 
#

###############################################################################
#############  Functions for on_startup() and on_shutdown() ###################
###############################################################################

async def on_startup():
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

async def on_shutdown():
    # Create shutdown actions if needed
    pass

###############################################################################
####################  Initialize app, user, client Functions ##################
###############################################################################

async def initialize_app(q: Q):
    """
    Initialize the app. Code here is run once at the app level.
    """
    logging.info('Initializing app')
    q.app.initialized = True

    # q.app.flex: use flexible layout rather than grid
    #  - Development: start with Cartesian grid then move to flex
    #  - Flex looks better in general but it's easier to develop with grid
    q.app.flex = True 

    # debug codes
    q.app.debug = True
 
    ## upload logo
    q.app.umgc_logo, = await q.site.upload(['umgc-logo-white.png'])

    # set global default first term
    q.app.default_first_term = 'Spring 2024'

    # SHORTCUT: Added these into the view directly, will fix this code later
    # as we fix the logic for these, will remove from disabled
    q.app.disabled_program_menu_items = {
        'Cybersecurity Technology',
        'Social Science',
        'Applied Technology',
        'Web and Digital Design',        
        'East Asian Studies',
        'English',
        'General Studies',
        'History'
    }

    await q.page.save()

async def initialize_user(q: Q):
    """
    Initialize the user.

    - Keep database connections at the user level, rather than app (once per program run) 
      or client (once per browser tab).
    - Intend to have multiple users connecting simultaneously
    """
    logging.info('Initializing user')
    q.user.initialized = True
    q.user.conn = utils.TimedSQLiteConnection('UMGC.db')

    ## Until logged in, user is a guest
    #q.user.role = 'guest'
    #q.user.logged_in = False 

    await utils.reset_student_info_data(q)

    q.user.user_id = 5
    q.user.role == 'student'
    await utils.populate_student_info(q, q.user.user_id)
    q.user.student_info_populated = True

    # Note: All user variables related to students will be saved in a dictionary
    # q.user.student_info
    #
    # This will allow us to keep track of student information whether the role is admin/coach 
    # (where we can easily switch students by deleting q.user.student_info and starting over), or
    # student/guest roles (with single instance of q.user.student_info).
    #
    # For example, if q.user.user_id=2 is a coach working on a student with user_id=3, then we
    # populate q.user.student_info['user_id']=3 with that student's information.
    #
    # Student information stored in q.user.student_info
    #   - role in ('admin', 'coach') will start from new student or populate with saved
    #     student info using 'select student' dropdown menu (later will be lookup)
    #   - role == 'student' will start new or from saved student info from database
    #   - role == 'guest' will always start new

    await q.page.save()

async def initialize_client(q: Q):
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = cards.return_meta_card()
    q.page['header'] = cards.return_header_card(q)
    #q.page['header'] = cards.return_login_header_card(q)
    q.page['footer'] = cards.return_footer_card(q)

#    if q.app.debug:
#        q.page['debug'] = ui.markdown_card(box=ui.box('debugcards.return_debug_card(q)

    await q.page.save()
    if q.args['#'] is None:
        await home(q)

###############################################################################
##################  End initialize app, user, client Functions ################
###############################################################################


######################################################
####################  Login page  ####################
######################################################

@on('#login')
async def login(q: Q):
    clear_cards(q)
    card_height = '400px'

    #q.page['header'] = cards.return_login_header_card(q)
    #cards.render_welcome_back_card(q, width='400px', height=card_height, location='top_vertical')

    #cards.render_login_welcome_card(q, cardname='welcome_login', location='top_horizontal')
    card = cards.return_login_welcome_card(q, location='top_horizontal', width='100%')
    add_card(q, 'login/welcome', card)

    card = await cards.return_user_login_dropdown(q, location='horizontal', menu_width='300px')
    add_card(q, 'login/demo_login', card)

    if q.app.debug:
        q.page['debug'] = await cards.return_debug_card(q)

    await q.page.save()

# respond to sample user selection
@on()
async def select_sample_user(q: Q):
    '''
    Respond to sample user selection from cards.render_user_dropdown
    '''
    choice = q.args.choice_group
    logging.info('The selected user is: ' + choice)
    q.user.user_id = int(choice)
    
    # initialize all student_info stuff
    await utils.reset_student_info_data(q)
    q.user.student_info_populated = False

    # Guest has user_id = 0
    if q.user.user_id > 0:
        q.user.logged_in = True
        # get role for logged in user
        await utils.set_user_vars_given_role(q) # assigns q.user.role_id, q.user.username, q.user.name

        # Admin path:
        #   - Can add users
        #   - Can set or change user roles
        #   - Can do other administrative tasks
        #   - Can do everything a coach can do
        #
        # Coach path:
        #   - Can add students
        #   - Using pulldown menu to select student,
        #     can profile, select program, select courses, schedule courses for students
        #
        # Student path:
        #   - Can profile, select program, select courses, schedule courses for themselves
        #
        # Guest path:
        #   - Can do everything a student can do except save their info to the database 
        #
        if q.user.role in ['coach', 'admin']:
            pass
        elif q.user.role == 'student':
            await utils.populate_student_info(q, q.user.user_id)
            q.user.student_info_populated = True

    else:
        # guest mode
        #await utils.reset_student_info_data(q) # already done?
        pass

    # update header 
    q.page['header'] = cards.return_header_card(q)
    if q.user.role == 'guest':
        # to do: replace the guest item in header with student name
        pass

    # update debug card
    if q.app.debug:
        q.page['debug'].content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.user.student_info values:
{q.user.student_info}

### q.user values:
{q.user}
        '''

    # redirect to #home route
    q.page['meta'].redirect = '#home'    
        
    await q.page.save()

######################################################
####################  Home page  #####################
######################################################

@on('#home')
async def home(q: Q):
    clear_cards(q)
    card_height = '400px'

    # this depends on student stage:


    #cards.render_home_cards(q)

    # By definition, students are registered so we at least know their name

    if int(q.user.student_info['app_stage_id']) == 1:
        card = cards.return_task1_card(location='top_horizontal', width='350px')
        add_card(q, 'home/task1', card=card)

        card = cards.return_demographics_card1(location='top_horizontal', width='400px')
        add_card(q, 'home/demographics1', card)

        card = cards.return_tasks_card(checked=0, location='top_horizontal', width='350px', height='400px')
        add_card(q, 'home/tasks', card)

    elif int(q.user.student_info['app_stage_id']) == 2:
        card = cards.return_welcome_back_card(q, location='top_horizontal', height='400px', width='750px')
        add_card(q, 'home/welcome_back', card=card)

        card = cards.return_tasks_card(checked=1, location='top_horizontal', width='350px', height='400px')
        add_card(q, 'home/tasks', card)

    elif int(q.user.student_info['app_stage_id']) == 3:
        card = cards.return_welcome_back_card(q, location='top_horizontal', height='400px', width='750px')
        add_card(q, 'home/welcome_back', card=card)

        card = cards.return_tasks_card(checked=2, location='top_horizontal', width='350px', height='400px')
        add_card(q, 'home/tasks', card)

    else:
        card = cards.return_welcome_back_card(q, location='top_horizontal', height='400px', width='750px')
        add_card(q, 'home/welcome_back', card=card)

        card = cards.return_tasks_card(checked=4, location='top_horizontal', width='350px', height='400px')
        add_card(q, 'home/tasks', card)

    await q.page.save()

@on('#home/1')
async def home1(q: Q):
    clear_cards(q)

    card = cards.return_task1_card(location='top_horizontal', width='350px')
    add_card(q, 'home/task1', card=card)

    cards.demographics2(q)
    cards.tasks_unchecked(q)

    await q.page.save()


@on('#home/2')
async def home2(q: Q):
    clear_cards(q)

    #add_card(q, 'ai_enablement', return_ai_enablement_card(location='horizontal'))
    #await cards.render_interest_assessment_card(q, location='horizontal', width='33%')
    #await cards.render_personality_assessment_card(q, location='horizontal', width='33%')

    cards.task2(q)
    await cards.render_skills_assessment_card(q, location='top_horizontal', width='33%')

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
async def register_submit(q):
    '''
    Respond to submission button on registration page 
    (from render_registration_card(q))
    '''
    q.user.guest_info = {
        'firstname': q.args.firstname,
        'lastname': q.args.lastname,
        'fullname': q.args.firstname + ' ' + q.args.lastname
    }
    q.user.student_info['name'] = q.user.guest_info['fullname']

    q.page['registration'].items = [
        #ui.text_xl('Welcome to the UMGC Registration Assistant'),
        ui.text_xl(f'Thank you, {q.user.guest_info["firstname"]}! You are now registered.'),
        #ui.text(f'First Name: {q.user.guest_info["firstname"]}'),
        #ui.text(f'Last Name: {q.user.guest_info["lastname"]}'),
        #ui.text(f'Full Name: {q.user.guest_info["fullname"]}'),
    ]

    await q.page.save()

@on()
async def next_demographic_1(q):
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
async def next_demographic_2(q):
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

async def admin_program(q: Q):
    await student_program(q)

async def coach_program(q: Q):
    await student_program(q)

async def student_program(q: Q):

    clear_cards(q)
    if q.user.student_info['menu']['degree']:
        degree_id = int(q.user.student_info['menu']['degree'])

    add_card(q, 'explore_programs', ui.form_card(
        box=ui.box('top_vertical', width='100%'),
        items=[
            ui.text('**EXPLORE PROGRAMS** using the menus below. Click **Select > Save Program** to select your program.'),
            #ui.text('Explore Majors. Click **Select > Save Program** to select your program.'),
        ]
    ))    
    await cards.render_dropdown_menus_horizontal(q, location='top_vertical', menu_width='300px')

    if q.user.student_info['program_id']:
        await cards.render_program(q)

#    if menu_degree == 1:
#        # Associate's Degree
#        clear_cards(['explore_programs', 'dropdown']) # clear all but the 
#        #await cards.render_program_description(q, location='top_vertical', height='250px', width='100%')
#        pass
#
#    elif menu_degree == 2: 
#        # Bachelor's Degree
#        clear_cards(['explore_programs', 'dropdown']) # clear all but the 
#        await cards.render_program_description(q, location='top_vertical', height='250px', width='100%')
#        await cards.render_program_table(q, location='horizontal', width='90%')
#        await cards.render_program_dashboard(q, location='horizontal', width='150px')
#
#    elif menu_degree == 5: 
#        # Undergraduate Certificate
#        pass
#
#    else:
#        # Graduate Certificate
#        pass


async def guest_program(q: Q):
    await student_program(q)

@on('#program')
async def program(q: Q):
    clear_cards(q) # will use in the individual functions

    if q.user.role == 'admin':
        # admin program page
        await admin_program(q)

    elif q.user.role == 'coach':
        # coach program page
        await coach_program(q)
        
    elif q.user.role == 'student':
        # student program page
        await student_program(q)
        
    else:
        # guest program page
        await guest_program(q)
    
    if q.app.debug_program:
        add_card(q, 'program_debug', await cards.return_debug_card(q))

    await q.page.save()

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

### q.user.student_info values:
{q.user.student_info}

### q.user values:
{q.user}
'''
    return content

#######################################
## For "Degree" dropdown menu events ##
#######################################

@on()
async def menu_degree(q: Q):
    logging.info('The value of menu_degree is ' + str(q.args.menu_degree))
    timedConnection = q.user.conn
    q.user.student_info['menu']['degree'] = q.args.menu_degree

    # reset area_of_study if degree changes
    q.user.student_info['menu']['area_of_study'] = None
    q.page['dropdown'].menu_area.value = None
    # update area_of_study choices based on degree chosen
    q.page['dropdown'].menu_area.choices = await get_choices(timedConnection, cards.area_query, 
        params=(q.user.student_info['menu']['degree'],))

    # reset program if degree changes
    utils.reset_program(q)

    if q.user.student_info['menu']['degree'] == '2':
        # insert ge into student_info for bachelor's degree students
        q.user.student_info['ge'] = utils.initialize_ge()
        pass
    else:
        #clear_cards(q, ['dropdown']) # clear everything except dropdown menus
        # remove ge from non-bachelor's degree students
        if 'ge' in q.user.student_info:
            del q.user.student_info['ge']

    q.page['program.debug'].content = dropdown_debug(q)
    await q.page.save()

##############################################
## For "Area of Study" dropdown menu events ##
##############################################

@on()
async def menu_area(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.menu_area))
    timedConnection = q.user.conn
    q.user.student_info['menu']['area_of_study'] = q.args.menu_area

    # reset program if area_of_study changes
    utils.reset_program(q)

    q.user.student_info['menu']['program'] = None
    q.page['dropdown'].menu_program.value = None

    # update program choices based on area_of_study chosen
    q.page['dropdown'].menu_program.choices = await get_choices(timedConnection, cards.program_query, 
        params=(q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study']))

#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

#    q.page['debug_info'] = cards.return_debug_card(q, box='1 10 7 4') # update debug card
    await q.page.save()

########################################
## For "Program" dropdown menu events ##
########################################

@on()
async def menu_program(q: Q):
    logging.info('The value of program is ' + str(q.args.menu_program))
    timedConnection = q.user.conn
    q.user.student_info['menu']['program'] = q.args.menu_program
    q.user.student_info['program_id'] = q.user.student_info['menu']['program']

    row = await utils.get_program_title(timedConnection, q.user.student_info['program_id'])
    if row:
        q.user.student_info['degree_program'] = row['title']
        q.user.student_info['degree_id'] = row['id']
    q.user.student_data['required'] = await utils.get_required_program_courses(q)

    # need to also update q.user.student_info['degree_program']
    logging.info('This is menu_program(q): the value of program_id is ' + str(q.user.student_info['program_id']))

    await cards.render_program(q)
    
    # # program_id an alias used throughout
    #result = await get_program_title(timedConnection, q.user.student_info['program_id'])
    #q.user.student_info['degree_program'] = result['title']
    #
    ## have the size of this depend on the degree (?)
    #if q.user.student_info['menu']['degree'] == '2':
    #    await cards.render_program(q)
    ##else:
    #    # Insert a blank card with a message - "has to be completed"

        ##await cards.render_program_description(q, box='1 3 7 2')
        ##await cards.render_program_dashboard(q, box='7 5 1 5') # need to fix
        ##await cards.render_program_coursework_table(q, box='1 5 6 5')

#    else:
#        clear_cards(q,['major_recommendations', 'dropdown'])
#        if hasattr(q.client, 'program_df'):
#            del q.client.program_df

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.return_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
#    q.page['debug_info'] = cards.return_debug_card(q, box='1 10 7 4') # update debug card
    await q.page.save()


###############################
###  Program Table actions  ###
###############################

@on()
async def program_table(q: Q):
    '''
    Respond to events (clicking Course link or double-clicking row)
    in the table on Program page. This will display the course description
    by default.

    Notes:
      - q.args.table_name is set to [row_name]
      - the name of the table is 'program_table'
      - the name of the row is name = row['name']    
    '''
    coursename = q.args.program_table[0] 
    utils.course_description_dialog(q, coursename, which='required')
    logging.info('The value of coursename in program_table is ' + coursename)
    await q.page.save()

@on()
async def view_program_description(q: Q):
    '''
    Respond to the menu event 'Course Description'
    (Calls same function as program_table above)
    '''
    coursename = q.args.view_program_description
    utils.course_description_dialog(q, coursename, which='required')
    logging.info('The value of coursename in view_program_description is ' + str(coursename))
    await q.page.save()

@on()
async def add_ge(q: Q):
    '''
    Respond to the menu event 'Add GE'
    (redirect to GE page)
    '''
    logging.info('Redirecting to the GE page')
    q.page['meta'].redirect = '#ge'
    await q.page.save()


########################################################
####################  Course pages  ####################
########################################################

async def admin_course(q: Q):
    await student_course(q)

async def coach_course(q: Q):
    await student_course(q)

async def student_course(q: Q):
    if q.user.student_data['schedule'] is not None:
        add_card(q, 'courses_instructions', ui.form_card(
            box='top_horizontal',
            items=[
                ui.text('**Instructions**: You have selected courses. You may now add electives or view your schedule.')
            ]
        ))
        await cards.render_course_page_table_use(q, location='horizontal')

    await q.page.save()

async def guest_course(q: Q):
    await student_course(q)

@on('#course')
async def course(q: Q):
    clear_cards(q)

    if q.user.role == 'admin':
        # admin course page
        await admin_course(q)

    elif q.user.role == 'coach':
        # coach course page
        await coach_course(q)
        
    elif q.user.role == 'student':
        # student course page
        await student_course(q)
        
    else:
        # guest course page
        await guest_course(q)
        
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

async def guest_ge(q: Q):
    await student_ge(q)

@on('#ge')
@on('goto_ge')
async def ge(q: Q):
    clear_cards(q)

    if q.user.role == 'admin':
        # admin ge page
        await admin_ge(q)

    elif q.user.role == 'coach':
        # coach ge page
        await coach_ge(q)
        
    elif q.user.role == 'student':
        # student ge page
        await student_ge(q)
        
    else:
        # guest ge page
        await guest_ge(q)
        
    if q.app.debug:
        add_card(q, 'ge_debug', await cards.return_debug_card(q))

    await q.page.save()

###############
## GE Events ##
###############

def ge_debug_content(q):
    result = f'''
### q.user.student_info['ge'] values:

- Arts: {q.user.student_info['ge']['arts']}
- Beh: {q.user.student_info['ge']['beh']}
- Bio: {q.user.student_info['ge']['bio']}
- Comm: {q.user.student_info['ge']['comm']}
- Math: {q.user.student_info['ge']['math']}
- Res: {q.user.student_info['ge']['res']}

### q.args values:
{q.args}

### q.events values:
{q.events}

#### q.page['ge_bio']
{dir(q.page['ge_bio'])}

{ q.page['ge_bio'].items['ge_bio_1a'].value }

#### Whole GE
{q.user.student_info['ge']}

### q.client value:
{q.client}
'''
    return result


##########################################
## GE set variables from pulldown menus ##
##########################################

# (Worry about making this efficient later)

#############
## GE Arts ##  Works now, need to add updated sql query
#############

@on()
async def ge_arts_check(q: Q):
    # set nopre = True
    q.user.student_info['ge']['arts']['nopre'] = True
    await q.page.save()

@on()
async def ge_arts_1(q: Q):
    q.user.student_info['ge']['arts']['1'] = q.args.ge_arts_1
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_arts_2(q: Q):
    q.user.student_info['ge']['arts']['2'] = q.args.ge_arts_2
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Beh ##
############

@on()
async def ge_beh_check(q: Q):
    # set nopre = True
    q.user.student_info['ge']['beh']['nopre'] = True
    await q.page.save()

@on()
async def ge_beh_1(q: Q):
    q.user.student_info['ge']['beh']['1'] = q.args.ge_beh_1
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_beh_2(q: Q):
    q.user.student_info['ge']['beh']['2'] = q.args.ge_beh_2
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Bio ##
############

@on()
async def ge_bio_check(q: Q):
    # set nopre = True
    q.user.student_info['ge']['bio']['nopre'] = True
    await q.page.save()

async def handle_dropdown_change(q, changed_dropdown):
    '''
    When one of three menus is selected, clear the others and reset 
    to defaults
    '''
    dropdowns=['ge_bio_1a', 'ge_bio_1b', 'ge_bio_1c']
    dropdowns.remove(changed_dropdown)

    selected = changed_dropdown.split('_')[2]
    q.user.student_info['ge']['bio'][selected] = q.args[changed_dropdown]

    for dropdown in dropdowns:
        # reset menu options to default
        q.page['ge_req4'].items[dropdown].value = None
        # clear q.user.student_info['ge']['bio'][which]
        which = dropdown.split('_')[2]
        q.user.student_info['ge']['bio'][which] = None

    await q.page.save()

@on()
async def ge_bio_1a(q: Q):
    logging.info('The value of ge_bio_1a = ' + q.args.ge_bio_1a)
#    await handle_dropdown_change(q, 'ge_bio_1a')
#    q.page['ge_debug'].content = ge_debug_content
#    await q.page.save()

    q.user.student_info['ge']['bio']['1a'] = q.args.ge_bio_1a
    q.user.student_info['ge']['bio']['1b'] = None
    q.user.student_info['ge']['bio']['1c'] = None
    # reset dropdown menu items?
    #q.page['ge_bio'].


    q.page['ge_debug'].content = ge_debug_content(q)

    await q.page.save()

@on()
async def ge_bio_1b(q: Q):
    logging.info('The value of ge_bio_1b = ' + q.args.ge_bio_1b)
##    await handle_dropdown_change(q, 'ge_bio_1b')
##    q.page['ge_debug'].content = ge_debug_content
##    await q.page.save()
#   
    q.user.student_info['ge']['bio']['1a'] = None
    q.user.student_info['ge']['bio']['1b'] = q.args.ge_bio_1b
    q.user.student_info['ge']['bio']['1c'] = None
##    # reset dropdown menu items?

    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_bio_1c(q: Q):
    logging.info('The value of ge_bio_1c = ' + q.args.ge_bio_1c)
#    await handle_dropdown_change(q, 'ge_bio_1b')
#    q.page['ge_debug'].content = ge_debug_content
#    await q.page.save()

    q.user.student_info['ge']['bio']['1a'] = None
    q.user.student_info['ge']['bio']['1b'] = None
    q.user.student_info['ge']['bio']['1c'] = q.args.ge_bio_1c
#    # reset dropdown menu items?

    q.page['ge_debug'].content = ge_debug_content
    await q.page.save()

@on()
async def ge_bio_2(q: Q):
    q.user.student_info['ge']['bio']['2'] = q.args.ge_bio_2
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#############
## GE Comm ##  These all work !!!
#############

@on()
async def ge_comm_check(q: Q):
    # set nopre = True
    q.user.student_info['ge']['comm']['nopre'] = True
    await q.page.save()

@on()
async def ge_comm_1(q: Q):
    q.user.student_info['ge']['comm']['1'] = q.args.ge_comm_1
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_comm_2(q: Q):
    q.user.student_info['ge']['comm']['2'] = q.args.ge_comm_2
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_comm_3(q: Q):
    q.user.student_info['ge']['comm']['3'] = q.args.ge_comm_3
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_comm_4(q: Q):
    q.user.student_info['ge']['comm']['4'] = q.args.ge_comm_4
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#############
## GE Math ##  This works! 
#############

@on()
async def ge_math_check(q: Q):
    # set nopre = True
    q.user.student_info['ge']['math']['nopre'] = True
    await q.page.save()

@on()
async def ge_math_1(q: Q):
    q.user.student_info['ge']['math']['1'] = q.args.ge_math_1
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Res ##
############

@on()
async def ge_res_check(q: Q):
    # set nopre = True
    q.user.student_info['ge']['res']['nopre'] = True
    await q.page.save()

@on()
async def ge_res_1(q: Q):
    q.user.student_info['ge']['res']['1'] = q.args.ge_res_1
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_2(q: Q):
    q.user.student_info['ge']['res']['2'] = q.args.ge_res_2
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_3(q: Q):
    q.user.student_info['ge']['res']['3'] = q.args.ge_res_3
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_3a(q: Q):
    q.user.student_info['ge']['res']['3a'] = q.args.ge_res_3a
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_3b(q: Q):
    q.user.student_info['ge']['res']['3b'] = q.args.ge_res_3b
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_3c(q: Q):
    q.user.student_info['ge']['res']['3c'] = q.args.ge_res_3c
    # reset dropdown menu items?
    q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

##########################################################
####################  Schedule pages  ####################
##########################################################

async def admin_schedule(q: Q):
    await student_schedule(q)

async def coach_schedule(q: Q):
    await student_schedule(q)

async def student_schedule(q: Q):
    if q.user.student_data['schedule'] is not None:
        # need to check whether all terms and sessions are all 0,
        # meaning a schedule template was created but no classes
        # were actually scheduled

        html_template = utils.create_html_template(
            df = q.user.student_data['schedule'], 
            start_term = q.user.student_info['first_term']
        )
        #add_card(q, 'd3plot', cards.render_d3plot(html_template, location='horizontal', width='80%'))
        await cards.render_d3plot(q, html_template, location='horizontal', width='75%', height='400px')
        await cards.render_schedule_menu(q, location='horizontal', width='20%')
        await cards.render_schedule_page_table(q, location='bottom_horizontal', width='100%')

async def guest_schedule(q: Q):
    await student_schedule(q)

@on('#schedule')
async def schedule(q: Q):
    clear_cards(q)

    # first term is required for all scheduling
    # this should create the default for the pulldown 'First Term' menu
    if q.user.student_info['first_term'] is None:
        q.user.student_info['first_term'] = q.app.default_first_term

    if q.user.role == 'admin':
        # admin schedule page
        await admin_schedule(q)

    elif q.user.role == 'coach':
        # coach schedule page
        await coach_schedule(q)
        
    elif q.user.role == 'student':
        # student schedule page
        await student_schedule(q)
        
    else:
        # guest schedule page
        await guest_schedule(q)

    #if q.app.debug:
    #    add_card(q, 'schedule_debug', await cards.return_debug_card(q))
        
    await q.page.save()

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
    q.user.student_info['schedule_menu'] = schedule_menu

    q.user.student_data['periods'] = utils.generate_periods(
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

### q.user.student_info values:
{q.user.student_info}

### q.user.student_info['schedule_menu'] values:
{q.user.student_info['schedule_menu']}

### q.user.student_data values:

#### Required:
{q.user.student_data['required']}

#### Periods:
{q.user.student_data['periods']}

#### Schedule:
{q.user.student_data['schedule']}
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
    utils.course_description_dialog(q, coursename, which='schedule')
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
    utils.course_description_dialog(q, coursename, which='schedule')
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

############################
## Dismiss dialog actions ##
############################

@on('my_dialog.dismissed')
@on('schedule_table.dismissed')
@on('schedule_description_dialog.dismissed')
@on('program_table.dismissed')
@on('required_description_dialog.dismissed')
async def dismiss_dialog(q: Q):
    logging.info('Dismissing dialog')
    q.page['meta'].dialog = None
    await q.page.save()

## below is a dummy function for demonstration
@on()
async def show_dialog(q: Q):
    # Create a dialog with a close button
    delete.example_dialog(q)
    await q.page.save()

# mode='multicast' sync information across all tabs of a user
# see https://wave.h2o.ai/docs/realtime
@app('/', mode='multicast', on_startup=on_startup)
async def serve(q: Q):

    # Initialize the app if not already
    if not q.app.initialized:
        await initialize_app(q)

    # Initialize the user if not already
    if not q.user.initialized:
        await initialize_user(q)

    # Initialize the client if not already
    if not q.client.initialized:
        await initialize_client(q)

    # Handle routing.
    await run_on(q)
    await q.page.save()


### Move the below to the right place

#@app('/login')
#async def login(q: Q):
#    if 'token' not in q.client:
#        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
#            ui.text_l('Please login'),
#            ui.button(name='login', label='Login', primary=True)
#        ])
#    else:
#        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
#            ui.text_l(f'Hello, {q.client.user["preferred_username"]}'),
#            ui.button(name='logout', label='Logout', primary=True)
#        ])
#    await q.page.save()
#
#@app('/callback')
#async def callback(q: Q):
#    code = q.args['code']
#    result = msal_app.acquire_token_by_authorization_code(
#        code,
#        scopes=SCOPE,
#        redirect_uri=REDIRECT_URI
#    )
#    if 'access_token' in result:
#        q.client.token = result['access_token']
#        userinfo_endpoint = os.getenv('REQUESTS_GET_ADDRESS')
#        q.client.user = requests.get(
#            userinfo_endpoint,
#            headers={'Authorization': f'Bearer {q.client.token}'}
#        ).json()
#        await serve(q)
#    else:
#        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
#            ui.text_l('Login failed. Please try again.')
#        ])
#        await q.page.save()
#
#@app('/')
#async def serve(q: Q):
#    if q.args.login:
#        auth_url = msal_app.get_authorization_request_url(
#            SCOPE, redirect_uri=REDIRECT_URI
#        )
#        q.page['redirect'] = ui.redirect(auth_url)
#    elif q.args.logout:
#        q.client.token = None
#        q.client.user = None
#        await login(q)
#    else:
#        await login(q)
