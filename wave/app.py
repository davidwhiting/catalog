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

## May be useful for creating tables from dataframe
## Rewrite my courses table below to try this out
def df_to_rows(df: pd.DataFrame):
    return [ui.table_row(str(row['ID']), [str(row[name]) for name in column_names]) for i, row in df.iterrows()]

def search_df(df: pd.DataFrame, term: str):
    str_cols = df.select_dtypes(include=[object])
    return df[str_cols.apply(lambda column: column.str.contains(term, case=False, na=False)).any(axis=1)]

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

conn = sqlite3.connect('UMGC.db')
c = conn.cursor()

#c.execute("SELECT * FROM progress WHERE student_id=?", (student_id_value,))

student_name_query = '''
    SELECT users.firstname || ' ' || users.lastname AS 'name'
        FROM users 
        INNER JOIN student_info ON users.id = student_info.user_id 
        WHERE student_info.id = {}
'''

# Pick this up from login activity
student_info_id = 0 # Guest profile, default
student_info_id = 3 # student with transfer credit
student_info_id = 1 # new student

student_name = single_query(student_name_query.format(student_info_id), c)    
student_progress_query = 'SELECT * FROM student_progress WHERE student_info_id={}'.format(student_info_id)

# reading student progress directly into pandas
df_raw = pd.read_sql_query(student_progress_query, conn)
#df = pd.read_sql_query("SELECT * FROM student_progress WHERE student_id=?", conn, params=(student_id_value,))

course_summary = df_raw.groupby(['type','completed']).agg(
    n=('credits', 'count'),
    total=('credits', 'sum')
).reset_index()

# pick up start_term from the form
start_term = 'SPRING 2024'

# may need to rewrite this for later
# df and headers contain information for the d3 diagram
df_d3, headers = utils.prepare_d3_data(df_raw, start_term.upper())

# df_raw contains information for the class table in courses tab
# I am currently converting to a dictionary, perhaps not needed
df_raw = df_raw.merge(headers[['period', 'name']].rename(columns={'name': 'term'}), on='period', how='left')

student_progress_records = df_raw.to_dict('records')

terms_remaining = max(headers.period)
completion_date = headers.loc[headers['period'] == terms_remaining, 'name'].values[0].capitalize()
total_credits_remaining = df_d3['credits'].sum()
credits_next_term = headers.loc[headers['period'] == 1, 'credits'].values[0]

# Convert to json for passing along to our d3 function
#json_data = df_d3.to_json(orient='records')

tuition = {
    'in_state': 324,
    'out_of_state': 499,
    'military': 250
}

cost_per_credit = tuition['military']
total_cost_remaining = "${:,}".format(total_credits_remaining * cost_per_credit)
next_term_cost = "${:,}".format(credits_next_term * cost_per_credit)

# Convert to json for passing along to our d3 function
df_json = df_d3.to_json(orient='records')
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

    new_image_path, = await q.site.upload(['images/program_overview_bmgt.png'])
    add_card(q, 'example_program_template', ui.image_card(
        box=ui.box('d3', height='500px', width='80%'),
#        box=ui.box('vertical', width='100%', height='400px'), 
        type='png',
        title="Bachelor's in Business Administration Program Overview",
        #caption='Lorem ipsum dolor sit amet consectetur adipisicing elit.',
        #category='Category',
        #label='Click me',
        #image='https://images.pexels.com/photos/3225517/pexels-photo-3225517.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260',
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

# Create columns for our courses table
course_columns = [
    ui.table_column(name='seq', label='Seq', sortable=True, data_type='number'),
    ui.table_column(name='name', label='Course', sortable=True, searchable=True, max_width='300', cell_overflow='wrap'),
    ui.table_column(name='credits', label='Credits'),
    ui.table_column(name='type', label='Type', min_width='170px', 
        cell_type=ui.tag_table_cell_type(name='type', tags=[
            ui.tag(label='MAJOR', color='$blue'),
            ui.tag(label='REQUIRED', color='$red'),
            ui.tag(label='GENERAL', color='$green'),
            ui.tag(label='ELECTIVE', color='$yellow')
        ])
    ),
    ui.table_column(name='term', label='Term', searchable=True),
    ui.table_column(name='session', label='Session', data_type='number')
]

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
#    add_card(q, 'table', cards.test_table())

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

async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()

async def initialize_client(q: Q) -> None:
    q.page['meta'] = cards.meta
    image_path, = await q.site.upload(['images/umgc-logo.png'])
    tmp_image_path, = await q.site.upload(['images/program_overview_bmgt.png'])
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
            await initialize_client(q)
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
