import logging
from h2o_wave import main, app, Q, ui, on, run_on, data, handle_on
from typing import Optional, List
import random

# 'templates' contains static html, markdown, and javascript D3 code
import templates

# cards contains static cards and python functions that render cards
import cards
from cards import add_card, clear_cards, meta_card, header_card, render_debug_card, render_debug_client_card, \
    get_choices, area_query, render_home_cards

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
    render_home_cards(q, location='top_horizontal')

    #q.page['example'] = ui.form_card(box='1 1 2 2', items=[
    #    ui.choice_group(
    #        name='choice_group',
    #        label='Choice group',
    #        value='A',
    #        choices=[
    #            ui.choice('A', 'Selected A'),
    #            ui.choice('B', 'Option B'),
    #            ui.choice('C', 'Option C'),
    #        ]
    #    )
    #])

    user_roles = ['Guest', 'Student', 'Counselor', 'Admin']
    add_card(q, 'home1', ui.form_card(
        box=ui.box('middle_horizontal', width='250px'),
        items=[
            ui.choice_group(
                name='user_role_choice_group',
                label='User Role',
                inline=False,
                choices=[ui.choice(name=x, label=x) for x in user_roles],
                value='Guest',
            )
        ]
    ))
    student_type = ["Associate", "Bachelor's", "Master's", "Doctorate"]
    add_card(q, 'student_type_card', ui.form_card(
        box=ui.box('middle_horizontal', width='250px'),
        items=[
            ui.choice_group(
                name='student_type',
                label='Student Type',
                inline=False,
                choices=[ui.choice(name=x, label=x) for x in student_type],
                value=q.client.student_type if (q.client.student_type is not None) else q.args.student_type,
            )
        ]
    ))
    tuition_type = ['In-State', 'Out-of-State', 'Military']
    add_card(q, 'tuition_type_card', ui.form_card(
        box=ui.box('middle_horizontal', width='250px'),
        items=[
            ui.choice_group(
                name='tuition_type',
                label='Tuition Type',
                inline=False,
                choices=[ui.choice(name=x, label=x) for x in tuition_type],
                value=q.client.tuition_type if (q.client.tuition_type is not None) else q.args.tuition_type,
            )
        ]
    ))
    attendance_type = ['Full-Time', 'Part-Time', 'Evening']
    add_card(q, 'attendance_type_card', ui.form_card(
        box=ui.box('middle_horizontal', width='250px'),
        items=[
            ui.choice_group(
                name='attendance_type',
                label='Attendance Type',
                inline=False,
                choices=[ui.choice(name=x, label=x) for x in attendance_type],
                value=q.client.attendance_type if (q.client.attendance_type is not None) else \
                    q.args.attendance_type,
            )
        ]
    ))
    student_profile_type = ['First time attending', 'Previous experience', 'Transfer credits']
    add_card(q, 'student_profile_type_card', ui.form_card(
        box=ui.box('middle_horizontal', width='250px'),
        items=[
            ui.choice_group(
                name='student_profile_type',
                label='Student Profile',
                inline=False,
                choices=[ui.choice(name=x, label=x) for x in student_profile_type],
                value=q.client.student_profile_type if (q.client.student_profile_type is not None) else \
                    q.args.student_profile_type,
            )
        ]
    ))
    #add_card(q, 'home5', ui.form_card(
    #    box=ui.box('middle_horizontal', width='250px'),
    #    items=[
    #        ui.text('Basic student info', size=ui.TextSize.XL),
    #        ui.text('Checkbox with **first time**, **previous experience**, **transfer credits**'),
    #    ]
    #))

    cards.render_debug(q, location='bottom_horizontal', width='33%')

###########################################################

@on('#major')
async def major(q: Q):
    clear_cards(q)  
    add_card(q, 'dropdown',
        await cards.render_dropdown_menus(q, location='top_horizontal', menu_width='300px'))

    add_card(q, 'major_recommendations',
        cards.render_major_recommendation_card(q, location='top_horizontal'))

    add_card(q, 'major1', ui.form_card(
        box=ui.box('top_horizontal', width='250px'),
        items=[
            ui.text('Compare Majors', size=ui.TextSize.XL),
            ui.text('Add **Compare Majors** functionality'),
        ]
    ))


    cards.render_debug(q, location='bottom_horizontal', width='33%')

###########################################################

@on('#course')
async def course(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    if q.user.degree_program:
        add_card(q, 'selected_program',
           ui.form_card(
               box='top_vertical',
               items=[ui.text(q.user.degree_program, size=ui.TextSize.XL)]
        ))
    else:
        add_card(q, 'selected_program',
           ui.form_card(
               box='top_vertical',
               items=[ui.text('Degree program not yet selected.', size=ui.TextSize.L)]
        ))


    for i in range(4):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))
###########################################################

@on('#schedule')
async def schedule(q: Q):
    clear_cards(q)  
    await home(q)
#    pass
#    #add_card(q, 'major_recommendations', 
#    #    cards.render_major_recommendation_card(q, location='top_horizontal'))
#    #add_card(q, 'dropdown', 
#    #    await cards.render_dropdown_menus(q, location='top_horizontal', menu_width='280px'))
#    #cards.render_debug(q, location='bottom_horizontal', width='33%')
        
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
    # need to learn how to close the connection when a user leaves

    # get user information
    query = '''
        SELECT role_id, username, firstname, lastname, firstname || ' ' || lastname AS name
        FROM users
        WHERE id = ?
    '''

async def initialize_client(q: Q):
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = meta_card()
    q.page['header'] = header_card(q)
    q.page['footer'] = cards.footer

    if q.args['#'] is None:
        await home(q)

@on()
async def degree(q: Q):
    logging.info('The value of degree is ' + str(q.args.degree))
    q.user.degree = q.args.degree
    if q.user.degree != '2':
        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
        del q.user.major_coursework_df
    # reset area_of_study if degree changes
    q.user.area_of_study = None 
    q.page['dropdown'].area_of_study.value = q.user.area_of_study
    # reset program if degree changes
    q.user.program = None 
    q.page['dropdown'].program.value = q.user.program

    q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.user.degree,))

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def area_of_study(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.degree))
    q.user.area_of_study = q.args.area_of_study
    if q.user.degree != '2':
        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
        del q.user.major_coursework_df

    # reset program if area_of_study changes
    q.user.program = None 
    q.page['dropdown'].program.value = q.user.program
    q.page['dropdown'].program.choices = await get_choices(q, cards.program_query, (q.user.degree, q.user.area_of_study))

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def program(q: Q):
    logging.info('The value of program is ' + str(q.args.degree))
    q.user.program = q.args.program
    q.user.program_id = q.user.program # program_id an alias used throughout
    q.user.degree_program = await utils.get_program_title(q, q.user.program_id)

    # display major dashboard
    if q.user.degree == '2':
        await cards.render_major_dashboard(q, location='middle_vertical')
        await cards.render_majors_coursework(q, location='middle_vertical')
    else:
        clear_cards(q,['major_recommendations', 'dropdown'])
        del q.user.major_coursework_df

    # get program name

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

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
