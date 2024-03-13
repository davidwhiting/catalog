from h2o_wave import main, app, Q, site, ui, on, handle_on, run_on, data, connect, copy_expando, graphics as g
import logging

import sqlite3
import pandas as pd
import json
import os.path

# app additions
import cards
import templates
import utils

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

# mode='broadcast' if we want to sync across all users 
#       (e.g., counselor and student logged in simultaneously)
# mode='multicast' if we want to sync all tabs for one user
@app('/', mode='multicast')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """

    try:
        # Initialize the app if not already
        if not q.app.initialized:
            await initialize_app(q)

        ## Will need to add for the future
        ## Initialize the user if not already
        #if not q.user.initialized:
        #    await initialize_user(q)

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
        #    await initialize_client(q)
            await initialize_client(q)
#            if q.args['#'] is None:
#                await home(q)

        # Delegate query to query handlers
        elif await handle_on(q):
            pass

        # This condition should never execute unless there is a bug in our code
        # Adding this condition here helps us identify those cases (instead of seeing a blank page in the browser)
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))

## check this, may be needed !!!!

    ## Handle routing.
    #await run_on(q)
    #await q.page.save()


async def initialize_app(q: Q):
    """
    Initialize the app.
    """

    logging.info('Initializing app')

    # Add app-level initialization logic here (loading datasets, database connections, etc.)
    #q.app.cards = ['main']

    conn = sqlite3.connect('UMGC.db')
    c = conn.cursor()

    # Mark as initialized at the app level (global to all clients)
    q.app.initialized = True

#async def initialize_user(q: Q):
#    """
#    Initialize the user.
#    """
#
#    logging.info('Initializing user')
#
#    # Add user-level initialization logic here (not sure what that is ...)
#    q.user.cards = ['main']
#
#    # Mark as initialized at the app level (global to all clients)
#    q.user.initialized = True

async def initialize_client(q:Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    logo_image, = await q.site.upload(['images/umgc-logo.png'])
    q.page['header'] = cards.header(logo_image, q)
    q.page['footer'] = cards.footer

    # Add more cards to the page

    # Mark as initialized at the client (browser tab) level
    q.client.initialized = True

    # Save the page
    await q.page.save()

#def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
#    """
#    Remove all the cards related to navigation.
#    """
#
#    logging.info('Clearing cards')
#
#    if not q.client.cards:
#        return
#
#    for name in q.client.cards.copy():
#        if name not in ignore:
#            del q.page[name]
#            q.client.cards.remove(name)


def clear_cards(q: Q, card_names: list):
    """
    Clear cards from the page.
    """

    logging.info('Clearing cards')

    for card_name in card_names:
        del q.page[card_name]


async def show_error(q: Q, error: str):
    """
    Displays errors.
    """

    logging.error(error)

    # Clear all cards
    clear_cards(q, q.app.cards)

    # Format and display the error
    q.page['error'] = cards.crash_report(q)

    await q.page.save()

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
    # this is still not working, how to maintain dropdown values while navigating app
    if 'degree' in q.args:
        q.client.degree = q.args.degree
    if 'area_of_study' in q.args:
        q.client.area_of_study = q.args.area_of_study
    if 'major' in q.args:
        q.client.major = q.args.major
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

    new_image_path, = await q.site.upload(['images/program_overview_bmgt.png'])
    add_card(q, 'example_program_template', ui.image_card(
        box=ui.box('d3', height='500px', width='80%'),
        type='png',
        title="Bachelor's in Business Administration Program Overview",
        path=new_image_path,
    ))

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
    add_card(q, 'd3plot', cards.d3plot(html_template, 'd3'))
    
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

    # automatically group by term?
    # see https://wave.h2o.ai/docs/examples/table-groups
    add_card(q, 'course_table', ui.form_card(box='vertical', items=[
        ui.table(
            name='table',
            downloadable=True,
            resettable=True,
            groupable=True,
            columns=[
                #ui.table_column(name='seq', label='Seq', data_type='number'),
                ui.table_column(name='text', label='Course', searchable=True),
                ui.table_column(name='credits', label='Credits', data_type='number'),
                ui.table_column(
                    name='tag', 
                    label='Course Type', 
                    filterable=True, 
                    cell_type=ui.tag_table_cell_type(
                        name='tags',
                        tags=[
                            ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                            ui.tag(label='REQUIRED', color='$red'),
                            ui.tag(label='GENERAL', color='#046A38'),
                            ui.tag(label='MAJOR', color='#1565C0'),
                        ]
                    )
                ),
                ui.table_column(name='term', label='Term', filterable=True),
                ui.table_column(name='session', label='Session', data_type='number'),
                ui.table_column(name='actions', label='Actions',
                    cell_type=ui.menu_table_cell_type(name='commands', commands=[
                        ui.command(name='reschedule', label='Change Schedule'),
                        ui.command(name='prerequisites', label='Show Prerequisites'),
                        ui.command(name='description', label='Course Description'),
                        #ui.command(name='delete', label='Delete'),
                    ])
                )

            ],
            rows=[ui.table_row(
                name=str(record['seq']),
                cells=[
                    #str(record['seq']), 
                    record['name'], 
                    str(record['credits']), 
                    record['type'].upper(), 
                    record['term'], 
                    str(record['session'])
                ]
            ) for record in student_progress_records]
        )
    ]))

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

@on('reload')
async def reload_client(q: Q):
    """
    Reset the client (browser tab).
    This function is called when the user clicks "Reload" on the crash report.
    """

    logging.info('Reloading client')

    # Clear all cards
    clear_cards(q, q.app.cards)

    # Reload the client
    await initialize_client(q)


async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    This function should never get called unless there is a bug in our code or query handling logic.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()

## do I need a logout or disconnect method?
## close the connection - this is not working here, where should it go?
#conn.close()
