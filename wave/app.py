from h2o_wave import main, app, Q, site, ui, on, run_on, data, connect, graphics as g

from typing import Optional, List
import logging

import sqlite3
import pandas as pd
import json
import os.path

import templates
import cards
import utils

from utils import add_card, single_query

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

## Create a database connection using wave
#connection = connect(key_id='uzer', key_secret='pa55word')
# Automatically creates a new database if it does not exist.
#db = connection["UMGC"]

# Pick this up from login activity
student_info_id = 0 # Guest profile

student_info_id = 1

## Using vanilla sqlite3, convert to wavedb later

conn = sqlite3.connect('db/UMGC.db')

student_name_query = '''
    SELECT users.firstname || ' ' || users.lastname AS 'name'
        FROM users 
        INNER JOIN student_info ON users.id = student_info.user_id 
        WHERE student_info.id = {}
'''

cur = conn.cursor()

#def single_query(query, cursor):
#    # convenience function for sqlite3 db queries that return one value
#    cursor.execute(query)
#    q_result = cursor.fetchone()
#    if q_result is not None:
#        result = q_result[0]
#    else:
#        result = None
#
#    return result

student_name = single_query(student_name_query.format(student_info_id), cur)

student_progress_query = 'SELECT * FROM student_progress WHERE student_info_id={}'.format(student_info_id)

df = pd.read_sql_query(student_progress_query, conn)

# Import the json file into a dataframe
# Backup 
#df = pd.DataFrame(templates.data_json_new)


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
    
    #for i in range(4):
    #    add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='250px'), name='', title='Tile',
    #                                              caption='Lorem ipsum dolor sit amet'))
    add_card(q, 'home_markdown1', 
        ui.form_card(
#            box=ui.box('vertical', height='600px'),
            box=ui.box('grid', width='400px'),
           items=[ui.text(templates.home_markdown1)]
        )
    )
    add_card(q, 'home_markdown2', 
        ui.form_card(
#            box=ui.box('vertical', height='600px'),
            box=ui.box('grid', width='400px'),
           items=[ui.text(templates.home_markdown2)]
        )
    )


@on('#major')
async def major(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'dropdown_menus', cards.dropdown_menus(q))
    add_card(q, 'stats1', ui.form_card(box='dashboard', items=[
        ui.stats(
#            justify='between', 
            items=[
                ui.stat(
                    label='Credits', 
                    value=str(total_credits_remaining), 
                    caption='Credits Remaining', 
                    icon='LearningTools'),            
                ui.stat(
                    label='Terms Remaining', 
                    value=str(terms_remaining), 
                    caption='Terms Remaining', 
                    icon='Education'),
                ui.stat(
                    label='Finish Date', 
                    value=completion_date, 
                    caption='(Estimated)', 
                    icon='SpecialEvent'),
                ui.stat(
                    label='Total Tuition', 
                    value=total_cost_remaining, 
                    caption='Estimated Tuition', 
                    icon='Money'),
            ]
        )
    ]))

    add_card(q, 'major_step0', ui.wide_info_card(
        box=ui.box('grid', width='400px'), 
        name='major_step0', 
        title="Populate BA/BS Database",
        caption="Add all Bachelor's Programs to database. Note discrepancies between UMGC website and catalog.")
    )
    add_card(q, 'major_step1', ui.wide_info_card(
        box=ui.box('grid', width='400px'), 
        name='major_step1', 
        title='Connect Database',
        caption='Connect backend database of major programs to menus.')
    )
    add_card(q, 'major_step2', ui.wide_info_card(
        box=ui.box('grid', width='400px'), 
        name='major_step2', 
        title='Browse Majors',
        caption='Add a "Browse Majors" functionality. Comparison shop majors. "Compare up to 3", etc.')
    )
    add_card(q, 'major_step3', ui.wide_info_card(
        box=ui.box('grid', width='400px'), 
        name='major_step3', 
        title='Recommend Major - Shortest',
        caption='Suggest Major(s) based on quickest/cheapest to finish.')
    )
    add_card(q, 'major_step4', ui.wide_info_card(
        box=ui.box('grid', width='400px'), 
        name='major_step4', 
        title='Recommend Major - People like me',
        caption='Suggest Major(s) based on recommendation engine.')
    )
#    add_card(q, 'major_step5', ui.wide_info_card(
#        box=ui.box('grid', width='400px'), 
#        name='major_step5', 
#        title='Title',
#        caption='Lorem ipsum dolor sit amet')
#    )

    #for i in range(4):
    #    add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
    #                                              caption='Lorem ipsum dolor sit amet'))


#    add_card(q, 'table0', cards.test_table())

@on('#courses')
async def courses(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
#    add_card(q, 'dropdown_menus', cards.dropdown_menus(q))
    # Generate the following automatically
    selected_degree = "Bachelor's"
    selected_program = "Business Administration"
    add_card(q, 'selected_major', 
        ui.form_card(
            box='horizontal',
            items=[
                ui.text(
                    selected_degree + ' in ' + selected_program,
                    size=ui.TextSize.XL
                )
            ]
        )
    )
    add_card(q, 'd3plot', cards.d3plot_new(html_template, 'd3'))
    
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
#    add_card(q, 'table', cards.test_table())
    
    add_card(q, 'edit_sequence', ui.wide_info_card(
        box=ui.box('grid', width='400px'), 
        name='', 
        title='Edit Sequence',
        caption='Add per-term control of course selection and sequence.'
    ))

    add_card(q, 'lock_courses', ui.wide_info_card(
        box=ui.box('grid', width='600px'), 
        name='', 
        title='Advice',
        caption='Add hints and advice from counselors, e.g., "Not scheduling a class for session 2 will delay your graduation by x terms"'
    ))

    add_card(q, 'stats', ui.form_card(box='dashboard', items=[
        ui.stats(
            #justify='between', 
            items=[
                ui.stat(
                    label='Tuition', 
                    value=next_term_cost, 
                    caption='Next Term Tuition', 
                    icon='Money'),
#            ], 
#            items=[
                ui.stat(
                    label='Credits', 
                    value=str(total_credits_remaining), 
                    caption='Credits Remaining', 
                    icon='LearningTools'),            
                ui.stat(
                    label='Terms Remaining', 
                    value=str(terms_remaining), 
                    caption='Terms Remaining', 
                    icon='Education'),
                ui.stat(
                    label='Finish Date', 
                    value=completion_date, 
                    caption='(Estimated)', 
                    icon='SpecialEvent'),
                ui.stat(
                    label='Total Tuition', 
                    value=total_cost_remaining, 
                    caption='Estimated Tuition', 
                    icon='Money'),
            ]
        )
    ]))

@on('#electives')
async def electives(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
#    add_card(q, 'table', cards.test_table())

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

# close the connection 
conn.close()