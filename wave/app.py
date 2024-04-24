from h2o_wave import main, app, Q, ui, on, run_on, data, handle_on

import logging
import pandas as pd
from typing import Optional, List
import random
import sqlite3

# 'templates' contains static html, markdown, and javascript D3 code
import templates

# cards contains static cards and python functions that render cards
import cards
from cards import add_card, clear_cards, get_choices
    #meta_card, render_debug_card
    #, render_debug_client_card
    #, area_query 
    #, render_home_cards

# 'utils' contains all other python functions
import utils
from utils import get_query, get_query_one

async def on_startup():
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

###########################################################

@on('#home')
async def home(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    add_card(q, 'welcome', ui.wide_info_card(
        #box=ui.box('top_horizontal', width='70%'),
        box='1 2 4 1',
        name='welcome',
        icon='Contact',
        title='Welcome to the UMGC Registration Assistant',
        caption='We will guide you through this experience.'
    ))

#    user_roles = ['Guest', 'Student', 'Counselor', 'Admin']
#    add_card(q, 'user_role_card', ui.form_card(
#        box=ui.box('middle_horizontal', width='250px'),
#        #style={'background': '#fdbf38'},
#        items=[
#            ui.dropdown(
#                name='user_role',
#                label='Select User Role',
#                value=q.client.user_role if (q.client.user_role is not None) else \
#                    'Guest', #q.args.user_role,
#                trigger=True,
#                width='200px',
#                choices=[ui.choice(name=x, label=x) for x in user_roles],
#            ),
#        ]
#    ))
#
#    ## If a student, get information from the student_info table
#    #query = '''
#    #    SELECT resident_status_id, transfer_credits, financial_aid, stage, program_id, profile, notes
#    #    FROM student_info WHERE user_id = ?
#    #'''
#
#    # select resident status from database
#    # save to database
#    resident_status = ['In-State', 'Out-of-State', 'Military']
#    add_card(q, 'resident_status_card', ui.form_card(
#        box=ui.box('middle_horizontal', width='250px'),
#        items=[
#            ui.choice_group(
#                name='resident_status',
#                label='Resident Status',
#                inline=False,
#                choices=[ui.choice(name=x, label=x) for x in resident_status],
#                value=q.client.resident_status if (q.client.resident_status is not None) else q.args.resident_status,
#            )
#        ]
#    ))
#
#    attendance_type = ['Full-Time', 'Part-Time', 'Evening']
#    add_card(q, 'attendance_type_card', ui.form_card(
#        box=ui.box('middle_horizontal', width='250px'),
#        items=[
#            ui.choice_group(
#                name='attendance_type',
#                label='Attendance Type',
#                inline=False,
#                choices=[ui.choice(name=x, label=x) for x in attendance_type],
#                value=q.client.attendance_type if (q.client.attendance_type is not None) else \
#                    q.args.attendance_type,
#            )
#        ]
#    ))
#
#    student_profile_type = ['First time attending', 'Previous experience', 'Transfer credits']
#    add_card(q, 'student_profile_type_card', ui.form_card(
#        box=ui.box('middle_horizontal', width='250px'),
#        items=[
#            ui.choice_group(
#                name='student_profile_type',
#                label='Student Profile',
#                inline=False,
#                choices=[ui.choice(name=x, label=x) for x in student_profile_type],
#                value=q.client.student_profile_type if (q.client.student_profile_type is not None) else \
#                    q.args.student_profile_type,
#            )
#        ]
#    ))

#    add_card(q, 'assessments', cards.career_assessment_card)
#    add_card(q, 'major_recommendations',
#        cards.render_major_recommendation_card(q, location='bottom_horizontal'))
#
#    add_card(q, 'enable_ai', cards.ai_enablement_card)
# 
#    cards.render_debug(q, location='debug', width='33%')

###########################################################

@on('#major')
async def major(q: Q):
    clear_cards(q)  

    add_card(q, 'dropdown',
        await cards.render_dropdown_menus_horizontal(q, 
            box='1 2 7 1', 
            menu_width='280px'
        )
    )

    # if first time, add a blank card where table is 
    # and a blank card for credits
    #await render_program_dashboard(q, box='7 3 1 7')
    #await render_program_coursework_table(q, box='1 3 6 7')

#    #add_card(q, 'major1', ui.form_card(
#    #    box=ui.box('top_horizontal', width='250px'),
#    #    items=[
#    #        ui.text('Browse Majors', size=ui.TextSize.XL),
#    #        ui.text('State as **Browse Majors**'),
#    #        ui.text('Compare Majors', size=ui.TextSize.XL),
#    #        ui.text('Add **Compare Majors** functionality'),
#    #    ]
#    #))

    if hasattr(q.user, 'X_program'):
        if q.user.X_degree=='2': 
            await cards.render_program(q)


#    if q.client.major_debug:
#        cards.render_debug(q, location='debug', width='33%')

###########################################################

async def get_catalog_program_sequence(q):
    query = '''
        SELECT 
            a.seq, 
            a.course AS name,
            c.name as course_type,
            CASE
                WHEN INSTR(c.name, '_') > 0 
                THEN SUBSTR(c.name, 1, INSTR(c.name, '_') - 1)
                ELSE c.name
            END as type,
            b.credits,
            b.title,
            0 AS completed,
            0 AS term,
            0 AS session,
            0 AS locked,
            b.pre,
            b.pre_credits, 
            b.substitutions,
            b.description
        FROM 
            catalog_program_sequence a
        LEFT JOIN
            course_type c
        ON
            c.id = a.course_type_id
        LEFT JOIN
            classes b
        ON
            a.course = b.name
        WHERE 
            a.program_id = ?
    '''
    try:
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_program_id,))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or return a specific value or message

    # Check if df is empty
    if df.empty:
        print("The query returned zero rows.")
        return None  # or return a specific value or message

    return df

#async def get_catalog_program_sequence(q):
#    query = '''
#        SELECT seq, course FROM catalog_program_sequence WHERE program_id = ?
#    '''
#    df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_program_id,))
#    # check that df exists
#    return df

#async def get_student_progress(q):
#    query = '''
#        SELECT * FROM student_progress WHERE student_info_id = ?
#    '''
#    df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_student_info_id,))
#    # check that df exists
#    return df
    
async def get_student_progress(q):
    query = '''
        SELECT * FROM student_progress WHERE student_info_id = ?
    '''
    try:
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_student_info_id,))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or return a specific value or message

    # Check if df is empty
    if df.empty:
        print("The query returned zero rows.")
        return None  # or return a specific value or message

    return df

@on('#course')
async def course(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    # figure out conditions for program_selected to be true
    # before selecting courses, a program should be chosen
    if q.user.X_program is not None:
        await cards.render_program_description(q, box='1 2 7 2')
    else:
        print("select a program.") # put this in a card or redirect

    # starting to populate coursework... need to build this capability

    program_courses_built = True
    if program_courses_built:
        q.user.X_schedule_df = await get_student_progress(q)

    # check first that we are at the stage where this is available
    # instead of us having to build it. That stage is program_selected and catalog_selected. If
    # a schedule was ever created, we can retrieve it. 
    # if the_right_conditions_exist:
    
    
#    add_card(q, 'selected_program',
#        ui.form_card(
#        box='top_vertical',
#            items=[
#                ui.text(q.user.degree_program, size=ui.TextSize.XL) if q.user.degree_program else \
#                    ui.text('Degree program not yet selected.', size=ui.TextSize.L)
#            ]
#    ))
#
#    add_card(q, 'electives_tile', 
#        ui.wide_info_card(
#            box=ui.box('middle_horizontal', width='500px'),
#            name='', 
#            title='Explore Electives',
#            caption='Explore and perhaps recommend electives',
#    ))
#    add_card(q, 'minors_tile', 
#        ui.wide_info_card(
#            box=ui.box('middle_horizontal', width='500px'),
#            name='', 
#            title='Explore Minors',
#            caption='Explore and perhaps recommend minors',
#    ))
#   
#    cards.render_debug(q)

###########################################################

# GE should only show up if user.degree is Bachelor's. That navigation should show up in the Course tab.
@on('#ge')
@on('goto_ge')
async def ge(q: Q):
    clear_cards(q)

#    add_card(q, 'welcome_ge', ui.wide_info_card(
#        box=ui.box('top_horizontal', width='100%'),
#        name='welcome',
#        icon='Contact',
#        title='Select your General Education courses here.',
#        caption='We will guide you through this experience.'
#    ))
#
#    menu_width = '350px'
#
#    add_card(q, 'ge_req6', await cards.render_ge_research_card(q, menu_width, location='grid'))
#    add_card(q, 'ge_req1', await cards.render_ge_comm_card(q, menu_width, location='grid'))
#    add_card(q, 'ge_req4', await cards.render_ge_science_card(q, menu_width, location='grid'))
#    add_card(q, 'ge_req2', await cards.render_ge_math_card(q, menu_width, location='grid'))
#    add_card(q, 'ge_req3', await cards.render_ge_arts_card(q, menu_width, location='grid'))
#    add_card(q, 'ge_req5', await cards.render_ge_beh_card(q, menu_width, location='grid'))
#    
#    cards.render_debug(q)

###########################################################

@on('#electives')
async def electives(q: Q):
    clear_cards(q)
#    await ge(q)

###########################################################

@on('#schedule')
async def schedule(q: Q):
    clear_cards(q)

#    demo = True
#    Sessions = ['Session 1', 'Session 2', 'Session 3']
#    add_card(q, 'sessions_spin',
#        ui.form_card(
#            box=ui.box('middle_vertical', width='300px'),  # min width 200px
#            items=[
#                ui.dropdown(
#                    name='first_term',
#                    label='First Term',
#                    value='spring2024' if demo else q.args.first_term,
#                    trigger=True,
#                    width='150px',
#                    choices=[
#                        ui.choice(name='spring2024', label="Spring 2024"),
#                        ui.choice(name='summer2024', label="Summer 2024"),
#                        ui.choice(name='fall2024', label="Fall 2024"),
#                        ui.choice(name='winter2025', label="Winter 2025"),
#                    ]),
#                #                ui.separator(),
#                ui.checklist(
#                    name='checklist',
#                    label='Sessions Attending',
#                    choices=[ui.choice(name=x, label=x) for x in Sessions],
#                    values=['Session 1', 'Session 2', 'Session 3'],  # set default
#                ),
#                ui.spinbox(
#                    name='spinbox',
#                    label='Courses per Session',
#                    width='150px',
#                    min=1, max=5, step=1, value=1),
#                #                ui.separator(label=''),
#                ui.slider(name='slider', label='Max Credits per Term', min=1, max=16, step=1, value=9),
#                ui.inline(items=[
#                    ui.button(name='show_inputs', label='Submit', primary=True),
#                    ui.button(name='reset_sidebar', label='Reset', primary=False),
#                ])
#            ]
#        )
#    )
#
#    cards.render_debug(q)
#
##    await home(q)
##    pass
##    #add_card(q, 'major_recommendations', 
##    #    cards.render_major_recommendation_card(q, location='top_horizontal'))
##    #add_card(q, 'dropdown', 
##    #    await cards.render_dropdown_menus(q, location='top_horizontal', menu_width='280px'))
##    #cards.render_debug(q, location='bottom_horizontal', width='33%')
        
################################################################################

async def initialize_app(q: Q):
    """
    Initialize the app. Code here is run once at the app level.
    """
    q.app.initialized = True
    logging.info('Initializing app')

    # upload logo
    q.app.umgc_logo, = await q.site.upload(['images/umgc-logo-white.png'])


async def initialize_user(q: Q):
    """
    Initialize the user.

    - Keep database connections at the user level, rather than app (once per program run) 
      or client (once per browser tab).
    - In the future, will have multiple users connecting simultaneously

    To do: 
    - Replace sqlite3.connect with utils.TimesSQLiteConnection class. This will manage 
      open connections assuming a multiuser system. (A lightweight connection pool.)

    """
    logging.info('Initializing user')

    ## Initializing by deleting all variables in q.user. 
    ## Double check that this isn't breaking anything.
    #for key in list(q.user.keys()):
    #    delattr(q.user, key)

    q.user.initialized = True

    q.user.conn = sqlite3.connect('UMGC.db')
    # row_factory returns dictionaries rather than tuples
    # (more verbose, thus easier to understand code intent)
    q.user.conn.row_factory = sqlite3.Row  
    q.user.c = q.user.conn.cursor()

    #############################################################################
    ## keycloak implementation code found in utils.py goes here after updating ##
    #############################################################################

    #############
    ## Testing ##
    #############
    q.user.user_id = 0 # guest
    #q.user.user_id = 1 # admin
    #q.user.user_id = 2 # counselor
    #q.user.user_id = 3 # John Doe, student
    #q.user.user_id = 4 # Jane Doe, transfer student
    #q.user.user_id = 5 # Jim Doe, new student no major selected
    #q.user.user_id = 6 # Sgt Doe, military and evening student

    if q.user.user_id > 0:
        q.user.guest = False

        await cards.get_role(q)
        # add q.user.X_* updates if role is student
        if int(q.user.role_id) == 3:
            q.user.role = 'student'
            q.user.X_user_id = q.user.user_id
            q.user.X_name = q.user.name
    else:
        q.user.guest = True

    # Guest path:
    #   TBD (like student path, without saving) 
    #
    # Admin path:
    #   Can add users
    #   Can do other administrative tasks
    #
    # Counselor path:
    #   Can add students
    #   Using pulldown menu, can profile, select program, select courses, schedule courses for students
    #
    # Student path:
    #   Can profile, select program, select courses, schedule courses for themselves
    #

    # All user variables related to students will be denoted
    #   q.user.X_[name]
    # This will allow us to keep track of student information whether the path is admin/counselor or student
    # Otherwise, q.user.role_id=2 is counselor, but if the counselor is working on student with user_id=3, we
    # need to be able to denote that q.user.X_user_id=3, etc.
    
    # manual switch to test guest mode vs. other modes
    # will need an indicator from the app
    
    #q.user.logged_in = False 

    # retrieve information for logged-in user

    # note: student_info.id has a 1:1 mapping with user_id. May be better practice
    # to use user_id throughout (some tables contain student_info_id, some user_id).

    #if q.user.logged_in:
        #q.user.guest = False
        # q.user.user_id already created
                           # later add an "add student" functionality
        # if user is a student, do this:
    if q.user.role == 'student':
        await cards.get_student_info(q, q.user.X_user_id)
    #else:
    #    q.user.guest = True
    #    # create a random user_id for guest
    #    q.user.guest_id = random.randint(100000, 999999)

#    #    if not hasattr(q.user, 'records'):
#    #        q.user.ge_records = q.app.ge_records

async def initialize_client(q: Q):
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = cards.render_meta_card()
    q.page['header'] = cards.render_header(q)
    q.page['footer'] = cards.render_footer()

    # Debug status
    q.client.debug = True
    q.client.major_debug = False

    if q.args['#'] is None:
        await home(q)

@on()
async def user_role(q: Q):
    logging.info('The value of user_role is ' + str(q.args.user_role))
    q.user.user_role = q.args.user_role
#    #if q.user.degree != '2':
#    #    clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#    #    del q.client.program_df
#    ## reset area_of_study if degree changes
#    #q.user.area_of_study = None
#    #q.page['dropdown'].area_of_study.value = q.user.area_of_study
#    ## reset program if degree changes
#    #q.user.program = None
#    #q.page['dropdown'].program.value = q.user.program
#    #
#    #q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.user.degree,))
#    #
#    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#    q.page['debug_client_info'] = cards.render_debug_client_card(q)
#    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def degree(q: Q):
    logging.info('The value of degree is ' + str(q.args.degree))
    q.user.X_degree = q.args.degree
#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards

#        del q.client.program_df

    # reset area_of_study if degree changes
    q.user.X_area_of_study = None 
    q.page['dropdown'].area_of_study.value = q.user.X_area_of_study
    # reset program if degree changes
    q.user.X_program = None 
    q.page['dropdown'].program.value = q.user.X_program

    q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.user.X_degree,))

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def area_of_study(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.area_of_study))
    q.user.X_area_of_study = q.args.area_of_study
#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

    # reset program if area_of_study changes
    q.user.X_program = None 
    q.page['dropdown'].program.value = q.user.X_program
    q.page['dropdown'].program.choices = await get_choices(q, cards.program_query, (q.user.X_degree, q.user.X_area_of_study))

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def program(q: Q):
    logging.info('The value of program is ' + str(q.args.program))
    q.user.X_program = q.args.program
    q.user.X_program_id = q.user.X_program # program_id an alias used throughout
    q.user.X_degree_program = await utils.get_program_title(q, q.user.X_program_id)

    # display major dashboard and table
    if q.user.X_degree == '2':
        #clear_cards(q, ['dropdown'])
        await cards.render_program(q)

#    else:
#        clear_cards(q,['major_recommendations', 'dropdown'])
#        if hasattr(q.client, 'program_df'):
#            del q.client.program_df

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)

    await q.page.save()

@on()
async def program_table(q: Q):
    # note: q.args.table_name is set to [row_name]
    # the name of the table is 'program_table'
    # the name of the row is name=row['course'], the course name
    coursename = q.args.program_table[0]
    cards.render_dialog_description(q, coursename)
    logging.info('The value of coursename in program_table is ' + coursename)

@on()
async def view_description(q: Q):
    # Note: same function as program_table(q) called by view_description menu option
    coursename = q.args.view_description
    cards.render_dialog_description(q, coursename)
    logging.info('The value of coursename in view_description is ' + str(coursename))

@app('/', on_startup=on_startup)
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
