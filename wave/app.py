import logging
from h2o_wave import main, app, Q, ui, on, run_on, data, handle_on
from typing import Optional, List
import random

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
import sqlite3

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

#    #resident_status_check=q.client.resident_status if 
#    content=f''' 
#    Resident Status: {q.client.resident_status}
#
#    Attendance Type: {q.client.attendance_type}
#
#    '''

#    add_card(q, 'welcome2', ui.wide_info_card(
#        box=ui.box('top_horizontal', width='30%'),
#        name='welcome2',
#        icon='Contact',
#        title='Profile',
#        caption='Blank.'
#    ))

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
        await cards.render_dropdown_menus_horizontal(q, box='1 2 7 1', menu_width='280px')
    )

#    #add_card(q, 'major1', ui.form_card(
#    #    box=ui.box('top_horizontal', width='250px'),
#    #    items=[
#    #        ui.text('Browse Majors', size=ui.TextSize.XL),
#    #        ui.text('State as **Browse Majors**'),
#    #        ui.text('Compare Majors', size=ui.TextSize.XL),
#    #        ui.text('Add **Compare Majors** functionality'),
#    #    ]
#    #))

    if hasattr(q.user, 'program'):
        if q.user.degree=='2': 
            await cards.render_program(q)


#    if q.client.major_debug:
#        cards.render_debug(q, location='debug', width='33%')

###########################################################

@on('#course')
async def course(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

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

# GE should only show up if degree is Bachelor's. That navigation should show up in the Course tab.
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
        
###########################################################

async def initialize_app(q: Q):
    """
    Initialize the app.
    """
    q.app.initialized = True
    logging.info('Initializing app')

    # upload once
    q.app.umgc_logo, = await q.site.upload(['images/umgc-logo-white.png'])


async def initialize_user(q: Q):
    """
    Initialize the user.
    """
    logging.info('Initializing user')
    q.user.initialized = True
#    #keycloak_implemented = False

#    ##### KEYCLOAK CODE ##############
#    # temporary until keycloak login fully implemented
#    #    if keycloak_implemented:
#    #        #Decode the access token without verifying the signature
#    #        #Connects SSO to our user and student_info tables
#    #        user_details = jwt.decode(q.auth.access_token, options={"verify_signature": False})
#    #
#    #        q.user.username = user_details['preferred_username']
#    #        q.user.name = user_details['name']
#    #        q.user.firstname = user_details['given_name']
#    #        q.user.lastname = user_details['family_name']
#    #
#    # check whether user is in the sqlite3 db
#    # if so, get role and id
#    # if not, add user to db as a new student
#    #        q.user.user_id, q.user.role_id = utils.find_or_add_user(q)
#    #    else:
#    #        # fake it for now

    q.user.logged_in = False # need to test for this

    if q.user.logged_in:
        q.user.guest = False
        q.user.user_id = 1 # for the time being
    else:
        q.user.guest = True
        # create a random user_id for guest
        q.user.user_id = random.randint(100000, 999999)

    # keep database connections at the user level
    # future state: multiple users connecting simultaneously
    # tbd: replace connection with utils.TimesSQLiteConnection class
    q.user.conn = sqlite3.connect('UMGC.db')
    q.user.conn.row_factory = sqlite3.Row  # return dictionaries rather than tuples
    q.user.c = q.user.conn.cursor()

#    ## get user information
#    #query = '''
#    #    SELECT role_id, username, firstname, lastname, firstname || ' ' || lastname AS name
#    #    FROM users
#    #    WHERE id = ?
#    #'''
#
#    #row = query_row(query, (q.user.user_id,), q.app.c)
#    #(q.user.role_id, q.user.username, q.user.firstname, q.user.lastname, q.user.name) = row
#    #
#    ## If a student, get information from the student_info table
#    #query = '''
#    #    SELECT resident_status_id, transfer_credits, financial_aid, stage, program_id, profile, notes
#    #    FROM student_info WHERE user_id = ?
#    #'''
#    #if q.user.role_id == 1:
#    #    q.user.student = True
#    #    row = query_row(query, (q.user.user_id,), q.app.c)
#    #    (q.user.resident_status_id, q.user.transfer_credits, q.user.financial_aid, q.user.stage, q.user.program_id,
#    #     q.user.profile, q.user.notes) = row
#    #
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
    q.user.degree = q.args.degree
#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards

#        del q.client.program_df

    # reset area_of_study if degree changes
    q.user.area_of_study = None 
    q.page['dropdown'].area_of_study.value = q.user.area_of_study
    # reset program if degree changes
    q.user.program = None 
    q.page['dropdown'].program.value = q.user.program

    q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.user.degree,))

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def area_of_study(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.degree))
    q.user.area_of_study = q.args.area_of_study
#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

    # reset program if area_of_study changes
    q.user.program = None 
    q.page['dropdown'].program.value = q.user.program
    q.page['dropdown'].program.choices = await get_choices(q, cards.program_query, (q.user.degree, q.user.area_of_study))

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def program(q: Q):
    logging.info('The value of program is ' + str(q.args.degree))
    q.user.program = q.args.program
    q.user.program_id = q.user.program # program_id an alias used throughout
    q.user.degree_program = await utils.get_program_title(q, q.user.program_id)

    # display major dashboard and table
    if q.user.degree == '2':
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
