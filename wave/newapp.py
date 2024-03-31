import logging
from h2o_wave import main, app, Q, ui, on, run_on, data, handle_on
from typing import Optional, List
import random

import cards
from cards import add_card, clear_cards, meta_card, header_card, render_debug_card, render_debug_client_card, \
    get_choices, area_query, render_home_cards

import sqlite3

async def on_startup():
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

###########################################################

@on('#home')
async def home(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    await render_home_cards(q, location='middle_horizontal')

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

@on('#page3')
async def page3(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(12):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))

async def initialize_app(q: Q):
    """
    Initialize the app.
    """
    q.app.initialized = True
    logging.info('Initializing app')

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
    # potentially multiple users can connect at the same time
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
    # If no active hash present, render home.
    if q.args['#'] is None:
        await home(q)

@on()
async def degree(q: Q):
    logging.info('The value of degree is ' + str(q.args.degree))
    q.client.degree = q.args.degree
    q.page['dropdown'].area_of_study.choices = await get_choices(q, cards.area_query, (q.client.degree,))

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def area_of_study(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.degree))
    q.client.area_of_study = q.args.area_of_study
    q.page['dropdown'].program.choices = await get_choices(q, cards.program_query, (q.client.degree, q.client.area_of_study))

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

@on()
async def program(q: Q):
    logging.info('The value of program is ' + str(q.args.degree))
    q.client.program = q.args.program
    q.client.program_id = q.client.program

    # get program name
    #q.client.program_title = await cards.get_program_title(q, q.client.program_id)

    q.page['debug_info'] = cards.render_debug_card(q) # update debug card
    q.page['debug_client_info'] = cards.render_debug_client_card(q)
    q.page['debug_user_info'] = cards.render_debug_user_card(q)
    # create dashboard here with this
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
