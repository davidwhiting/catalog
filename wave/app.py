from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import logging
#import pandas as pd
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
# 
# Updated routing to include '#student/home', '#coach/home', '#admin/home', etc.
#   - admin role will be able to access all '#admin/...', '#coach/...' and '#student/...' pages
#   - coach role will be able to access all '#coach/...' and '#student/...' pages
#   - student role will be able to only access '#student/...' pages
#
# Some universal pages, like a login page, will thus be dubbed '#student/login' since it is 
# accessible by all.
#
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
    q.app.debug = True
 
    ## upload logo
    q.app.umgc_logo, = await q.site.upload(['umgc-logo-white.png'])
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
    q.user.student_info_populated = False # may be needed later 

    # if undergraduate degree, add ge by q.user.student_info['ge'] = utils.initialize_ge()

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

    # Until logged in, user is a guest
    q.user.role = 'guest'
    q.user.logged_in = False 

    # get role for logged in user
    await utils.get_role(q) # assigns q.user.role_id, q.user.username, q.user.name
    if q.user.role != 'guest':
        q.user.logged_in = True

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

    await q.page.save()

###############################################################################
##################  End initialize app, user, client Functions ################
###############################################################################

@on('#page1')
async def page1(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    await delete.page1_1(q)

@on('#page2')
async def page2(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    await delete.page2_1(q)

@on('#page3')
async def page3(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    await delete.page3_1(q)

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

@on('#student/login')
@on('#coach/login')
@on('#admin/login')
async def student_login(q: Q):
    await page2(q)

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

async def admin_admin(q: Q):
    pass

@on('#admin')
async def admin(q: Q):
    if q.user.role == 'admin':
        # admin page
        await admin_admin(q)

    else: 
        # coach, student, guest not allowed
        pass

    if q.app.debug:
        add_card(q, 'admin_debug', await cards.render_debug_card(q, width='100%'))

    await q.page.save()

######################################################
####################  Home pages  ####################
######################################################

async def admin_home(q: Q):
    await student_home(q)

async def coach_home(q: Q):
    await student_home(q)

async def student_home(q: Q):
    await page2(q)

async def guest_home(q: Q):
    await student_home(q)

@on('#home')
async def home(q: Q):
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
    await page1(q)

async def guest_program(q: Q):
    await student_program(q)

@on('#program')
async def program(q: Q):
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
    await page3(q)

async def guest_course(q: Q):
    await student_course(q)

@on('#course')
async def course(q: Q):
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
    await page3(q)

async def guest_schedule(q: Q):
    await student_schedule(q)

@on('#schedule')
async def schedule(q: Q):
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
        
    await q.page.save()

#####################################################
####################  End pages  ####################
#####################################################

@on('my_dialog.dismissed')
async def dismiss_dialog(q: Q):
    # Delete the dialog
    q.page['meta'].dialog = None
    await q.page.save()

@on()
async def show_dialog(q: Q):
    # Create a dialog with a close button
    delete.example_dialog(q)
    await q.page.save()

async def delete_initialize_client(q: Q) -> None:
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = cards.render_meta_card(flex=True)
    q.page['header'] = cards.render_header_card(q, flex=True)
    q.page['footer'] = cards.render_footer_card(q, flex=True)

    # If no active hash present, render home.
    if q.args['#'] is None:
        await home(q)

# mode='multicast' sync information across all tabs of a user
# see https://wave.h2o.ai/docs/realtime
@app('/catalog', mode='multicast', on_startup=on_startup)
async def serve(q: Q):

    # Initialize the app if not already
    if not q.app.initialized:
        await initialize_app(q)

    # Initialize the user if not already
    if not q.user.initialized:
        await initialize_user(q)

    # Initialize the client if not already
    if not q.client.initialized:
        await delete_initialize_client(q)
#        await initialize_client(q)

    # Handle routing.
    await run_on(q)
    await q.page.save()
