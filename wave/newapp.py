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
    render_home_cards(q, location='middle_horizontal')

    cards.render_debug(q, location='bottom_horizontal', width='33%')

###########################################################

@on('#major')
async def major(q: Q):
    clear_cards(q)  
    add_card(q, 'major_recommendations', 
        cards.render_major_recommendation_card(q, location='top_horizontal'))
    add_card(q, 'dropdown', 
        await cards.render_dropdown_menus(q, location='top_horizontal', menu_width='280px'))

    cards.render_debug(q, location='bottom_horizontal', width='33%')

###########################################################

@on('#course')
async def course(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(12):
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
    q.client.degree = q.args.degree
    # reset area_of_study if degree changes
    q.client.area_of_study = None 
    q.page['dropdown'].area_of_study.value = q.client.area_of_study
    # reset program if degree changes
    q.client.program = None 
    q.page['dropdown'].program.value = q.client.program

    q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.client.degree,))

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def area_of_study(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.degree))
    q.client.area_of_study = q.args.area_of_study
    # reset program if degree changes
    q.client.program = None 
    q.page['dropdown'].program.value = q.client.program
    q.page['dropdown'].program.choices = await get_choices(q, cards.program_query, (q.client.degree, q.client.area_of_study))

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def program(q: Q):
    logging.info('The value of program is ' + str(q.args.degree))
    q.client.program = q.args.program
    # save to user and get program name
    q.user.degree = q.client.degree
    q.user.area_of_study = q.client.area_of_study
    q.user.program = q.client.program
    q.user.program_id = q.user.program # program_id an alias used throughout
    q.user.degree_program = await utils.get_program_title(q, q.user.program_id)

    # display major dashboard
    await cards.render_major_dashboard(q, location='middle_vertical')
    await cards.render_majors_coursework(q, location='middle_vertical')
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
