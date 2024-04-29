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

    # get saved student information
    if q.user.role == 'student':
        await cards.get_student_info(q, q.user.X_user_id)

    # show this card only for guests and students with new status
    # for folks not yet logged in
#    if q.user.role == 'student' and q.user.X_app_stage_id > 1:
    if q.user.role == 'student':
        cards.render_welcome_back_card(q, box='1 2 3 4')
    else:
        cards.render_welcome_card(q)
        cards.render_please_login(q)

    add_card(q, 'dashboard_placeholder', ui.markdown_card(
        box='6 6 2 2',
        title='Dashboard',
        content='Add a summary dashboard here'
    ))

    add_card(q, 'to_do_next', ui.markdown_card(
        box='4 3 2 2',
        title='Next steps',
        content='Add links to continue, such as "Add Elective", "Update Schedule", etc.'
    ))

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

    add_card(q, 'assessments', cards.render_career_assessment_card(box='3 6 3 2'))
    add_card(q, 'major_recommendations',
             cards.render_major_recommendation_card(q, box='1 6 2 3'))
    add_card(q, 'enable_ai', cards.render_ai_enablement_card(box='3 8 3 2'))
    add_card(q, 'debug_home', cards.render_debug_user_card(q, box='2 10 6 4'))

##############################################################
###########  STUDENT PAGE                      ###############
##############################################################

##############################################################
###########  PROGRAM PAGE (PREVIOUSLY MAJOR)   ###############
##############################################################
@on('#major')
async def major(q: Q):
    clear_cards(q)  

    add_card(q, 'dropdown',
        await cards.render_dropdown_menus_horizontal(q, 
            box='1 2 7 1', 
            menu_width='300px'
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

    if hasattr(q.user, 'X_program_id'):
        await cards.render_program(q)
    # need to make available for degree types other than bachelor's

    #add_card(q, 'debug_program', cards.render_debug_user_card(q, box='1 10 7 2'))
    
##############################################################
####################  COURSES PAGE  ##########################
##############################################################
@on('#course')
async def course(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    # this is not working in guest mode now
    if hasattr(q.user, 'X_program_id'):
        # check whether schedule was previously created
        if hasattr(q.user, 'X_app_stage_id'):
            if q.user.X_app_stage_id is not None:
                stage_id=int(q.user.X_app_stage_id)
                if stage_id==4:
                    ## retrieve schedule from database
                    q.user.X_schedule_df = await cards.get_student_progress_d3(q)

                    add_card(q, 'courses_instructions', ui.form_card(
                        box='1 2 7 1',
                        items=[
                            ui.text('**Instructions**: You have selected courses. You may now add electives or view your schedule.')
                        ]
                    ))
                    await cards.render_course_page_table(q, q.user.X_schedule_df, box='1 3 7 7')

                else: # stage_id==3:
                    cards.render_courses_header(q, box='1 2 7 1')
                    # need to build a program from scratch
                    # ask whether to start by pulling from catalog suggested programs


        #await cards.render_program(q)

    # starting to populate coursework... need to build this capability

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

    #add_card(q, 'debug_course', cards.render_debug_user_card(q, box='1 9 7 2'))


##############################################################
####################  GE PAGE (START) ########################
##############################################################
@on('#ge')
@on('goto_ge')
async def ge(q: Q):
    clear_cards(q)

    add_card(q, 'welcome_ge', ui.form_card(
        box='1 2 7 1',
        items=[
            ui.text_l('Select your General Education courses here.'),
            #ui.text('We will guide you through this experience.')
        ]
    ))

    menu_width = '300px'
    add_card(q, 'ge_req1', await cards.render_ge_comm_card(q, menu_width, box='1 3 3 4'))
    add_card(q, 'ge_req6', await cards.render_ge_research_card(q, menu_width, box='4 3 3 6'))
    add_card(q, 'ge_req4', await cards.render_ge_science_card(q, menu_width, box='1 7 3 4'))
    add_card(q, 'ge_req2', await cards.render_ge_math_card(q, menu_width, box='4 9 3 2'))
    add_card(q, 'ge_req3', await cards.render_ge_arts_card(q, menu_width, box='1 11 3 3'))
    add_card(q, 'ge_req5', await cards.render_ge_beh_card(q, menu_width, box='4 11 3 3'))
 
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

    q.user.X_first_term = 'spring2024'
    demo = True # temporary fix

    ## Convert this to a function
    Sessions = ['Session 1', 'Session 2', 'Session 3']
                    
    if q.user.X_student_profile == 'Full-time':
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 12
        default_courses_per_session = 2
    else:
        default_sessions = ['Session 1', 'Session 2', 'Session 3']
        default_max_credits = 9
        default_courses_per_session = 1

    add_card(q, 'sessions_spin',
        ui.form_card(
            #box=ui.box('middle_vertical', width='300px'),  # min width 200px
            box='6 2 2 5',
            items=[
                ui.dropdown(
                    name='first_term',
                    label='First Term',
                    value='spring2024' if demo else q.args.first_term,
                    trigger=True,
                    width='150px',
                    choices=[
                        ui.choice(name='spring2024', label="Spring 2024"),
                        ui.choice(name='summer2024', label="Summer 2024"),
                        ui.choice(name='fall2024', label="Fall 2024"),
                        ui.choice(name='winter2025', label="Winter 2025"),
                    ]),
                #                ui.separator(),
                ui.checklist(
                    name='checklist',
                    label='Sessions Attending',
                    choices=[ui.choice(name=x, label=x) for x in Sessions],
                    values=default_sessions,  # set default
                ),
                ui.spinbox(
                    name='spinbox',
                    label='Courses per Session',
                    width='150px',
                    min=1, max=5, step=1, value=default_courses_per_session),
                #                ui.separator(label=''),
                ui.slider(name='slider', label='Max Credits per Term', min=1, max=16, step=1, 
                          value=default_max_credits),
                ui.inline(items=[
                    ui.button(name='show_inputs', label='Submit', primary=True),
                    ui.button(name='reset_sidebar', label='Reset', primary=False),
                ])
            ]
        )
    )

    # this should be carried over from previous step, or any changes in course should be 
    # written to DB, our source of truth
    df = await cards.get_student_progress_d3(q)
    q.user.X_schedule_df = df


    # Fix this to work with guest mode
    if hasattr(q.user, 'X_schedule_df'):
        add_card(q, 'schedule_instructions', ui.form_card(
            box='1 2 5 1',
            items=[
                ui.text(f'**{q.user.X_degree_program}**')
            ]
        ))
        await cards.render_schedule_page_table(q, box='1 7 7 6')

        ## display df
        start_term = 'Spring 2024' # pick this up from q.user variables
        # rename because the function uses 'period' rather than 'term'

        df_input = df.copy()
        df_input.rename(columns={'term': 'period'}, inplace=True)

        df_display, headers_display = utils.prepare_d3_data(df_input, start_term.upper())
        df_json = df_display.to_json(orient='records')
        headers_json = headers_display.to_json(orient='records')

        html_template = templates.html_code_minimal.format(
            javascript=templates.javascript_draw_only,
            headers=headers_json, 
            data=df_json)

        add_card(q, 'd3plot', cards.d3plot(html_template, box='1 3 5 4'))

        #######################################
        ## Scheduling and updating schedules ##
        #######################################

        # rescheduling given rules
        # pick these variables up from the form
        periods = utils.generate_periods(
            start_term='SPRING 2024', # pick up from q.user.X_ variable
            max_courses=3, # pick up from courses_per_session
            sessions=[1, 3], # pick up from 'Sessions Attending'
            summer=True, # attending summer? Add this to form!!
            length=30 # more than we need
        )
        q.user.X_periods = periods # save to variable

        # updating syntax for fine-tuning max_courses, max_credits, etc. 
        updated_periods = utils.update_periods(periods, 
            "term == 'SUMMER' and year == 2024", 
            {"max_courses": 0}
        )
        q.user.X_periods = updated_periods # save to variable
#


#    #add_card(q, 'debug_schedule', cards.render_debug_user_card(q, box='1 9 7 2'))
#    add_card(q, 'edit_sequence', ui.wide_info_card(
#        box=ui.box('grid', width='400px'), 
#        name='', 
#        title='Edit Sequence',
#        caption='Add per-term control of course selection and sequence.'
#    ))
#
#    add_card(q, 'lock_courses', ui.wide_info_card(
#        box=ui.box('grid', width='600px'), 
#        name='', 
#        title='Advice',
#        caption='Add hints and advice from counselors, e.g., "Not scheduling a class for session 2 will delay your graduation by x terms"'
#    ))


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

#############################################################
####################  PROJECT PAGE (START) ##################
#############################################################

@on('#project')
async def project(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    card = await cards.render_project_table(templates.project_data, box='1 2 7 9', height='700px')
    add_card(q, 'project_table_location', card)

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
    ### the above code is not working

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
    #q.user.user_id = 0 # guest
    #q.user.user_id = 1 # admin
    #q.user.user_id = 2 # counselor
    q.user.user_id = 3 # John Doe, student
    #q.user.user_id = 4 # Jane Doe, transfer student
    #q.user.user_id = 5 # Jim Doe, new student no major selected
    #q.user.user_id = 6 # Sgt Doe, military and evening student

    # Note: All user variables related to students will be denoted
    #   q.user.X_[name]
    # This will allow us to keep track of student information whether the path is admin/counselor or student
    # Otherwise, q.user.role_id=2 is counselor, but if the counselor is working on student with user_id=3, we
    # need to be able to denote that q.user.X_user_id=3, etc.

    if q.user.user_id == 0:
        q.user.guest = True
    else:
        q.user.guest = False

        await cards.get_role(q) # assigns q.user.role_id, q.user.username, q.user.name
        if str(q.user.role) == 'student':
            # add q.user.X_* updates if role is student
            q.user.X_user_id = q.user.user_id
            q.user.X_name = q.user.name

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
async def menu_degree(q: Q):
    logging.info('The value of menu_degree is ' + str(q.args.menu_degree))
    q.user.X_menu_degree = q.args.menu_degree
#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

    # reset area_of_study if menu_degree changes
    q.user.X_menu_area = None 
    q.page['dropdown'].area_of_study.value = q.user.X_menu_area
    # reset program if degree changes
    q.user.X_menu_program = None 
    q.page['dropdown'].menu_program.value = q.user.X_menu_program
    # update choices
    q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.user.X_menu_degree,))

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def menu_area(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.menu_area))
    q.user.X_menu_area = q.args.menu_area
#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

    # reset program if area_of_study changes
    q.user.X_menu_program = None 
    q.page['dropdown'].menu_program.value = q.user.X_menu_program
    q.page['dropdown'].menu_program.choices = await get_choices(q, cards.program_query, (q.user.X_menu_degree, q.user.X_menu_area))

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def menu_program(q: Q):
    logging.info('The value of program is ' + str(q.args.menu_program))
    q.user.X_menu_program = q.args.menu_program
    q.user.X_program_id = q.args.menu_program # program_id an alias used throughout
    q.user.X_degree_program = await utils.get_program_title(q, q.user.X_program_id)
    
    # have the size of this depend on the degree
    await cards.render_program(q)
    #await cards.render_program_description(q, box='1 3 7 2')
    #await cards.render_program_dashboard(q, box='7 5 1 5') # need to fix
    #await cards.render_program_coursework_table(q, box='1 5 6 5')

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

@on()
async def student_dropdown(q: Q):
    logging.info('The value of user_dropdown is ' + str(q.args.user_dropdown))
    #pass
    q.user.user_dropdown = q.args.user_dropdown
    #q.user.user_dropdown = q.args.user_dropdown # to check

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
