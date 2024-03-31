import logging
from h2o_wave import main, app, Q, ui, on, run_on, data, graphics as g
from typing import Optional, List

import cards2
from cards2 import add_card, meta_card, header_card, crash_report, render_fallback

import sqlite3
import pandas as pd
import json
import os.path

from utils import query_row

async def on_startup():
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

async def init(q: Q) -> None:
    q.page['meta'] = meta_card()
    q.page['header'] = header_card(q)

    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)

@app('/second', mode='unicast', on_startup=on_startup)
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

    ## Define the route handler for dropdown triggers
    #if q.args.triggered:
    #    # Check which dropdown triggered the update
    #    if q.args.degree.changed:
    #        # Update the choices for the 'Area of Study' dropdown based on the selected 'Degree'
    #        q.client.degree = q.args.degree
    #        q.page['area_of_study'].choices = await get_choices(q, cards2.area_query, (q.args.degree,))
    #    elif q.args.area_of_study.changed:
    #        # Update the choices for the 'Program' dropdown based on the selected 'Degree' and 'Area of Study'
    #        q.client.area_of_study = q.args.area_of_study
    #        q.page['major_program'].choices = await get_choices(q, cards2.program_query, (q.args.degree, q.args.area_of_study))

    # Handle routing.
    await run_on(q)
    await q.page.save()

#    # Update table if query is edited
#    elif q.args.query is not None and q.args.query != q.client.query:
#        await apply_query(q)
#
#    # Update dataset if changed
#    elif q.args.dataset is not None and q.args.dataset != q.client.dataset:
#        await update_dataset(q)
#

async def initialize_app(q: Q):
    """
    Initialize the app.
    """
    q.app.initialized = True
    logging.info('Initializing app')

    q.app.umgc_logo, = await q.site.upload(['images/umgc-logo-white.png'])
 
    # Set initial argument values
    #q.app.cards = ['main', 'error']

async def initialize_user(q: Q):
    """
    Initialize the user.
    """
    logging.info('Initializing user')
    q.user.initialized = True
    q.user.logged_in = False

    if q.user.logged_in:
        q.user.guest = False
        q.user.user_id = 1 # for the time being
    else:
        q.user.guest = True
        q.user.user_id = 0 # default guest user

    # keep database connections at the user level
    # potentially multiple users can connect at the same time
    q.user.conn = sqlite3.connect('UMGC.db')
    q.user.conn.row_factory = sqlite3.Row  # return dictionaries rather than tuples
    q.user.c = q.user.conn.cursor()
    # need to learn how to close the connection when a user leaves

async def initialize_client(q: Q):
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = meta_card()
    q.page['header'] = header_card(q)
    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)

async def show_error(q: Q, error: str):
    """
    Displays errors.
    """
    logging.error(error)

    # Clear all cards
    clear_cards(q, q.app.cards)

    # Format and display the error
    q.page['error'] = crash_report(q)

    await q.page.save()

async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    """
    logging.info('Adding fallback page')

    q.page['fallback'] = render_fallback()

    await q.page.save()

#@on('degree')
#async def degree(q: Q):
#    print(q.args.degree)
#    q.client.degree = q.args.degree

#    await q.page.save()

#    query = '''
#        SELECT DISTINCT menu_area_id AS name, area_name AS label 
#        FROM menu_all_view 
#        WHERE menu_degree_id = ?
#    '''
#    query = '''
#        SELECT DISTINCT menu_area_id AS name, area_name AS label 
#        FROM menu_all_view 
#        WHERE menu_degree_id = 2
#    '''
#    #q.user.c.execute(query, [q.args.degree])
#    q.user.c.execute(query)
#    rows=q.user.c.fetchall()
#    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
#    q.page['area_of_study'].items = choices



def render_debug_card_old(q, location='horizontal'):
    content = f'''
### q.args.degree value:
{q.args.degree}

### q.args.area_of_study value:
{q.args.area_of_study}

### App Parameters
{q.app}

### User Parameters
{q.user}

### Client Parameters
{q.client}
    '''
    return ui.markdown_card(box=location, title='Debugging Information', content=content )


#@on()
#async def major_program(q: Q):
#    q.client.major_program = q.args.major_program
#    q.client.area_of_study = q.args.area_of_study
#    q.client.degree = q.args.degree

@on('#page1')
async def page1(q: Q):
    clear_cards(q)  # When routing, drop all the cards except the main ones (header, sidebar, meta).
#    add_card(q, 'dropdown_test', render_program_dropdown_menus(q)) # doesn't work

 
    add_card(q, 'debug_info', render_debug_card(q)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q)) 
    for i in range(1):
        add_card(q, f'info{i}', 
            ui.tall_info_card(
                box='horizontal', name='', title='Speed',
                caption='The models are performant thanks to...', 
                icon='SpeedHigh'
            )
        )


@on('#page2')
async def page2(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'chart1', ui.plot_card(
        box='horizontal',
        title='Chart 1',
        data=data('category country product price', 10, rows=[
            ('G1', 'USA', 'P1', 124),
            ('G1', 'China', 'P2', 580),
            ('G1', 'USA', 'P3', 528),
            ('G1', 'China', 'P1', 361),
            ('G1', 'USA', 'P2', 228),
            ('G2', 'China', 'P3', 418),
            ('G2', 'USA', 'P1', 824),
            ('G2', 'China', 'P2', 539),
            ('G2', 'USA', 'P3', 712),
            ('G2', 'USA', 'P1', 213),
        ]),
        plot=ui.plot([ui.mark(type='interval', x='=product', y='=price', color='=country', stack='auto',
                              dodge='=category', y_min=0)])
    ))
    add_card(q, 'chart2', ui.plot_card(
        box='horizontal',
        title='Chart 2',
        data=data('date price', 10, rows=[
            ('2020-03-20', 124),
            ('2020-05-18', 580),
            ('2020-08-24', 528),
            ('2020-02-12', 361),
            ('2020-03-11', 228),
            ('2020-09-26', 418),
            ('2020-11-12', 824),
            ('2020-12-21', 539),
            ('2020-03-18', 712),
            ('2020-07-11', 213),
        ]),
        plot=ui.plot([ui.mark(type='line', x_scale='time', x='=date', y='=price', y_min=0)])
    ))
    add_card(q, 'table', ui.form_card(box='vertical', items=[ui.table(
        name='table',
        downloadable=True,
        resettable=True,
        groupable=True,
        columns=[
            ui.table_column(name='text', label='Process', searchable=True),
            ui.table_column(name='tag', label='Status', filterable=True, cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=[
                    ui.tag(label='FAIL', color='$red'),
                    ui.tag(label='DONE', color='#D2E3F8', label_color='#053975'),
                    ui.tag(label='SUCCESS', color='$mint'),
                ]
            ))
        ],
        rows=[
            ui.table_row(name='row1', cells=['Process 1', 'FAIL']),
            ui.table_row(name='row2', cells=['Process 2', 'SUCCESS,DONE']),
            ui.table_row(name='row3', cells=['Process 3', 'DONE']),
            ui.table_row(name='row4', cells=['Process 4', 'FAIL']),
            ui.table_row(name='row5', cells=['Process 5', 'SUCCESS,DONE']),
            ui.table_row(name='row6', cells=['Process 6', 'DONE']),
        ])
    ]))


@on('#page3')
async def page3(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(12):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))


@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    q.page['sidebar'].value = '#page4'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # If first time on this page, create the card.
    add_card(q, 'form', ui.form_card(box='vertical', items=[
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1'),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox1', label='Textbox 1'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step2', label='Next', primary=True),
        ]),
    ]))


@on()
async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]


@on()
async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]
