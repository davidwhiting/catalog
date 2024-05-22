from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import logging
import os
from msal import ConfidentialClientApplication
import requests
import pandas as pd
import numpy as np

#import random
#import sqlite3

import delete_me as delete

# 'templates' contains static html, markdown, and javascript D3 code
import templates
# cards contains static cards and python functions that render cards (render_... functions)
import cards
# 'utils' contains all other python functions
import utils
from utils import add_card, clear_cards

##########################################
#############  Update Notes ##############
##########################################

# Adding user authentication information, assuming an external OAuth2 or similar SSO service.
# Within the Wave app, users will be mapped to one of three roles: admin, coach, or student.
#   - Default roles from the SSO service may be used to map default SSO roles to Wave roles
#     (e.g., 'student' -> 'student', 'staff' -> 'coach', 'faculty' -> 'coach', etc.). 
#   - Another option is to map all new Wave users to 'student' and allow only the Wave admin 
#     to change user roles to 'coach' or 'admin'.
#
# Instructions for setting up a SSO docker for local development are now in the README.md file.
#
# Updated routing to include '#student/home', '#coach/home', '#admin/home', etc.
#   - admin role will be able to access all '#admin/...', '#coach/...' and '#student/...' pages
#   - coach role will be able to access all '#coach/...' and '#student/...' pages
#   - student role will be able to only access '#student/...' pages
#
# Some universal pages, like a login page, will thus be dubbed '#student/login' since it is 
# accessible by all.
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

    # Variables for SSO through Azure Ensure ID.
    #   'off' will turn SSO capability off 
    #   'local' is for local development using keycloak
    #   'azure' needs to be set before deployment

    q.app.sso = 'off'
    #q.app.sso = 'local'
    #q.app.sso = 'azure'
    if q.app.sso != 'off':
        if q.app.sso == 'local':
            AUTHORITY = 'http://localhost:8080/auth/realms/myrealm'
            REQUESTS_GET_ADDRESS = 'http://localhost:8080/auth/realms/myrealm/protocol/openid-connect/userinfo'
            CLIENT_ID = 'myclient'
            CLIENT_SECRET = 'hAtwNXiXg3d2Eg9VayWFusJo1UWQZGb3' # only works for local macbook pro
            #CLIENT_SECRET = os.getenv('CLIENT_SECRET')
            REDIRECT_URI = 'http://localhost:5000/callback'
        elif q.app.sso == 'azure':
            AUTHORITY = os.getenv('AUTHORITY_ADDRESS')
            REQUESTS_GET_ADDRESS = os.getenv('REQUESTS_GET_ADDRESS')
            CLIENT_ID = os.getenv('CLIENT_ID')
            CLIENT_SECRET = os.getenv('CLIENT_SECRET')
            REDIRECT_URI = os.getenv('REDIRECT_URI')

        q.app.SCOPE = ['openid', 'profile', 'email']
        q.app.msal_app = ConfidentialClientApplication(
            CLIENT_ID, 
            authority=AUTHORITY, 
            client_credential=CLIENT_SECRET
        )

    # q.app.flex: use flexible layout rather than grid
    #  - Development: start with Cartesian grid then move to flex
    #  - Flex looks better in general but it's easier to develop with grid
    q.app.flex = True 
    q.app.debug = True
 
    ## upload logo
    q.app.umgc_logo, = await q.site.upload(['umgc-logo-white.png'])

    # set global default first term
    q.app.default_first_term = 'spring2024'

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

    # Until logged in, user is a guest
    q.user.role = 'guest'
    q.user.logged_in = False 

    # Note: All user variables related to students will be saved in a dictionary
    # q.user.student_info
    #
    # This will allow us to keep track of student information whether the role is admin/counselor 
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

    q.user.student_info = utils.initialize_student_info()
    q.user.student_info['ge'] = utils.initialize_ge() # only if undergraduate
    q.user.student_info_populated = False # may be needed later 

    q.user.student_data = utils.initialize_student_data() # will have required, periods, schedule

    # Wrap this testing section in a pulldown menu
    # 
    #############
    ## Testing ##
    #############
    #q.user.user_id = 0 # guest
    #q.user.user_id = 1 # admin
    #q.user.user_id = 2 # coach
    q.user.user_id = 3 # John Doe, student
    #q.user.user_id = 4 # Jane Doe, transfer student
    #q.user.user_id = 5 # Jim Doe, new student no major selected
    #q.user.user_id = 6 # Sgt Doe, military and evening student

    ## The following code will usually be accessed via the login page
    # get role for logged in user
    await utils.set_user_vars_given_role(q) # assigns q.user.role_id, q.user.username, q.user.name
    if q.user.role != 'guest':
        q.user.logged_in = True

    # normally pass this in from the login page
    # we may initially not allow guests
    #if q.user.role != 'guest':
    #    q.user.logged_in = True

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

    if str(q.user.role) == 'student':
        #user_id = int(q.user.student_info['user_id'])
        q.user.student_info['user_id'] = q.user.user_id
        q.user.student_info['name'] = q.user.name
        await utils.populate_student_info(q, q.user.student_info['user_id'])
        q.user.student_info_populated = True

        q.user.student_data['user_id'] = q.user.user_id
        stage_id = int(q.user.student_info['app_stage_id'])
        if stage_id == 4:
            # retrieve previous schedule
            q.user.student_data['schedule'] = await utils.get_student_progress_d3(q)

    await q.page.save()

async def initialize_client(q: Q):
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = cards.render_meta_card(flex=True)
    q.page['header'] = cards.render_header_card(q, flex=True)
    q.page['footer'] = cards.render_footer_card(q, flex=True)

    if q.args['#'] is None:
        await home(q)

###############################################################################
##################  End initialize app, user, client Functions ################
###############################################################################

#@on('#page1')
#async def page1(q: Q):
#    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
#    await delete.page1_1(q)
#
#@on('#page2')
#async def page2(q: Q):
#    clear_cards(q)  
#    await delete.page2_1(q)
#
#@on('#page3')
#async def page3(q: Q):
#    clear_cards(q)  
#    await delete.page3_1(q)

#######################################################
####################  Page 4 page  ####################
#######################################################

@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    q.page['sidebar'].value = '#page4'
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # If first time on this page, create the card.
    await delete.page4_1(q)

@on()
async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    await delete.page4_2(q)

@on()
async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    await delete.page4_3(q)

######################################################
####################  Login page  ####################
######################################################

#@on('#login')
#async def login(q: Q):
#    clear_cards(q)
#    await page2(q)

## If login functions change, do the following:
#
#@on('#coach/login')
#async def coach_login(q: Q):
#    await student_login(q)
#
#@on('#admin/login')
#async def admin_login(q: Q):
#    await student_login(q)

######################################################
####################  Admin page  ####################
######################################################

#async def admin_admin(q: Q):
#    pass
#
#@on('#admin')
#async def admin(q: Q):
#    clear_cards(q)
#
#    if q.user.role == 'admin':
#        # admin page
#        await admin_admin(q)
#
#    else: 
#        # coach, student, guest not allowed
#        pass
#
#    if q.app.debug:
#        add_card(q, 'admin_debug', await cards.render_debug_card(q, width='100%'))
#
#    await q.page.save()

######################################################
####################  Home pages  ####################
######################################################

async def admin_home(q: Q):
    await student_home(q)

async def coach_home(q: Q):
    await student_home(q)

async def student_home(q: Q):
    clear_cards(q)

async def guest_home(q: Q):
    await student_home(q)

@on('#home')
async def home(q: Q):
    clear_cards(q)

    if q.user.role == 'admin':
        # admin home page
        await admin_home(q)

    elif q.user.role == 'coach':
        # coach home page
        await coach_home(q)
        
    elif q.user.role == 'student':
        # student home page
        await student_home(q)
        
    else:
        # guest home page
        await guest_home(q)

    if q.app.debug:
        add_card(q, 'home_debug', await cards.render_debug_card(q, width='100%'))
    
    await q.page.save()

#########################################################
####################  Program pages  ####################
#########################################################

async def admin_program(q: Q):
    await student_program(q)

async def coach_program(q: Q):
    await student_program(q)

async def student_program(q: Q):
    add_card(q, 'dropdown',
        await cards.render_dropdown_menus_horizontal(q, location='top_horizontal', menu_width='300px')
    )
    await q.page.save()

async def guest_program(q: Q):
    await student_program(q)

@on('#program')
async def program(q: Q):
    clear_cards(q)

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
    
    if q.app.debug:
        add_card(q, 'program_debug', await cards.render_debug_card(q, width='100%'))

    await q.page.save()

########################################################
####################  Course pages  ####################
########################################################

async def admin_course(q: Q):
    await student_course(q)

async def coach_course(q: Q):
    await student_course(q)

async def student_course(q: Q):
    pass

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
        
    if q.app.debug:
        add_card(q, 'course_debug', await cards.render_debug_card(q, width='100%'))

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
        await cards.render_d3plot(q, html_template, location='horizontal', width='85%', height='400px')
        await cards.render_schedule_menu(q, location='horizontal')
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

    if q.app.debug:
        add_card(q, 'schedule_debug', await cards.render_debug_card(q, width='100%'))
        
    await q.page.save()

### Table Menu Items
#@on()
#async def schedule_table.click(q: Q):
#    pass

############################
## Schedule table actions ##
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
