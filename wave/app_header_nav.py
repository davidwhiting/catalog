#from h2o_wave import main, app, Q, ui, on, run_on, data
from h2o_wave import main, app, Q, site, ui, on, run_on, data, graphics as g
from typing import Optional, List
import logging

import pandas as pd
import json
import os.path

import templates
import cards
import utils


from utils import add_card

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)


# Import the json file into a dataframe
# eventually we will extract this from the database
df = pd.DataFrame(templates.data_json_new)

# pick up start_term from the form
start_term = 'SPRING 2024'

df, headers = utils.prepare_d3_data(df, start_term.upper())

terms_remaining = max(headers.period)
completion_date = headers.loc[headers['period'] == terms_remaining, 'name'].values[0].capitalize()
total_credits_remaining = df['credits'].sum()
credits_next_term = headers.loc[headers['period'] == 1, 'credits'].values[0]

# Convert to json for passing along to our d3 function
#json_data = df.to_json(orient='records')

tuition = {
    'in_state': 324,
    'out_of_state': 499,
    'military': 250
}

cost_per_credit = tuition['military']
total_cost_remaining = "${:,}".format(total_credits_remaining * cost_per_credit)
next_term_cost = "${:,}".format(credits_next_term * cost_per_credit)

# Convert to json for passing along to our d3 function
df_json = df.to_json(orient='records')
headers_json = headers.to_json(orient='records')

html_template = templates.html_code_minimal.format(
    javascript=templates.javascript_minimal, 
    headers=headers_json, 
    data=df_json)
#    html_template = templates.html_code.format(javascript=d3_js_script_path, data=json_data)

# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)


@on('#home')
async def home(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    add_card(q, f'step1_of_n', 
        ui.tall_info_card(
            box=ui.box('horizontal', width='25%'), 
            name='Name', 
            title='Login',
            caption='The first step is to log in', 
            icon='Signin')
    )
    add_card(q, f'step2_of_n', 
        ui.tall_info_card(
            box=ui.box('horizontal', width='25%'), 
            name='', 
            title='Import Information',
            caption='Import student information from RDBMS. Information includes tuition type (military, in-state, out-of-state), persona, transfer credits, major chosen, classes completed, etc.', 
            icon='Import')
    )
    add_card(q, f'step3_of_n', 
        ui.tall_info_card(
            box=ui.box('horizontal', width='25%'), 
            name='', 
            title='Update Information',
            caption='Details to be filled in.', 
            icon='SpeedHigh')
    )
    add_card(q, f'step4_of_n', 
        ui.tall_info_card(
            box=ui.box('horizontal', width='25%'), 
            name='', 
            title='Personalization',
            caption='Details to be filled in.', 
            icon='UserFollowed')
    )

# credits remaining icon: LearningTools
    
    add_card(q, 'home_markdown', 
        ui.form_card(
            box=ui.box('vertical', height='600px'),
            items=[ui.text(templates.home_markdown)]
        )
    )

@on('#major')
async def major(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'dropdown_menus', cards.dropdown_menus(q))
    add_card(q, 'table1', ui.form_card(box='vertical', items=[ui.table(
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

@on('#courses')
async def courses(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'dropdown_menus', cards.dropdown_menus(q))
    add_card(q, 'd3plot', cards.d3plot_new(html_template, 'd3'))

#    add_card(q, 'sessions', 
#        ui.form_card(
#            box=ui.box('grid', width='400px'),
#            items=[
#                ui.checklist(
#                    name='checklist', 
#                    label='Sessions Attending',
#                    choices=[ui.choice(name=x, label=x) for x in ['Session 1', 'Session 2', 'Session 3']]),
#            #    ui.button(name='show_inputs', label='Submit', primary=True),
#        ])
#    )
    
#    add_card(q, 'spinbox', 
#        ui.form_card(
#            box=ui.box('grid', width='400px'),
#            items=[
#                ui.spinbox(name='spinbox', label='Courses per Session', min=1, max=5, step=1, value=1),
#            #    ui.button(name='show_inputs', label='Submit', primary=True),
#            ]
#        )
#    )
    Sessions = ['Session 1', 'Session 2', 'Session 3']
    add_card(q, 'sessions_spin', 
        ui.form_card(
            box=ui.box('d3', width='300px'), # min width 200px
            items=[
            #    ui.dropdown(
            #        name='first', 
            #        label='Start Term', 
            #        value=q.args.start_term,
            #        trigger=True,
            #        width='250px',
            #        choices=[
            #            ui.choice(label="Spring 2024"),
            #            ui.choice(label="Summer 2024"),
            #            ui.choice(label="Fall 2024"),
            #            ui.choice(label="Winter 2025"),
            #        ]
            #    ),
                ui.checklist(
                    name='checklist', 
                    label='Sessions Attending',
                    choices=[ui.choice(name=x, label=x) for x in Sessions],
                    values=Sessions, # set default
                ),
                ui.spinbox(
                    name='spinbox', 
                    label='Courses per Session', 
                    width='150px',
                    min=1, max=5, step=1, value=1),
#                ui.separator(label=''),
                ui.slider(name='slider', label='Max Credits per Term', min=1, max=15, step=1, value=9),
                ui.button(name='show_inputs', label='Submit', primary=True),
            ]
        )
    )
    add_card(q, 'table', cards.test_table())

@on('#electives')
async def electives(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'table', cards.test_table())

    for i in range(4):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))


@on('#student')
@on('student_reset')
async def student(q: Q):
    q.page['sidebar'].value = '#student'
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
            ui.button(name='student_step2', label='Next', primary=True),
        ]),
    ]))

@on()
async def student_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='student_step3', label='Next', primary=True),
        ])
    ]

@on()
async def student_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='student_reset', label='Finish', primary=True),
        ])
    ]

async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()

async def initialize_client_old(q: Q) -> None:
    q.page['meta'] = cards.meta_new
    image_path, = await q.site.upload(['umgc-logo.png'])
    q.page['header'] = cards.header_new(image_path, q)
    q.page['footer'] = cards.footer

    # If no active hash present, render home.
    if q.args['#'] is None:
        await home(q)

#        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],

async def show_error(q: Q, error: str):
    """
    Displays errors.
    """
## Fix in the future
## Need to adapt from Waveton
#    logging.error(error)
#
#    # Clear all cards
#    clear_cards(q, q.app.cards)
#
#    # Format and display the error
#    q.page['error'] = cards.crash_report(q)
#
#    await q.page.save()


@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """

    try:
        # Run only once per client connection.
        if not q.client.initialized:
            q.client.cards = set()
            await initialize_client_old(q)
            q.client.initialized = True

        # Adding this condition to help in identifying bugs
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))

    # Handle routing.
    await run_on(q)
    await q.page.save()

#@app('/')
#async def serve(q: Q):
#    """
#    Main entry point. All queries pass through this function.
#    """
#
#    try:
#        # Initialize the app if not already
#        if not q.app.initialized:
#            await initialize_app(q)
#
#        # Initialize the client if not already
#        if not q.client.initialized:
#            await initialize_client(q)
#
#        # Update theme if toggled
#        elif q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
#            await update_theme(q)
#
#        # Update table if query is edited
#        elif q.args.query is not None and q.args.query != q.client.query:
#            await apply_query(q)
#
#        # Update dataset if changed
#        elif q.args.dataset is not None and q.args.dataset != q.client.dataset:
#            await update_dataset(q)
#
#        # Delegate query to query handlers
#        elif await handle_on(q):
#            pass
#
#        # Adding this condition to help in identifying bugs
#        else:
#            await handle_fallback(q)
#
#    except Exception as error:
#        await show_error(q, error=str(error))
