from h2o_wave import main, app, Q, site, ui, on, run_on, data, connect, graphics as g

from typing import Optional, List
import logging

import sqlite3
import pandas as pd
import jwt
import json
import os.path

# templates contains static html, markdown, and javascript D3 code
import templates
# cards contains static cards and functions that render cards
import cards
# utils contains all other functions
import utils

from utils import add_card, single_query

async def on_startup():
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

#def on_shutdown():

# Moved to q.app
# connect sqlite3
conn = sqlite3.connect('UMGC.db')
c = conn.cursor()

#c.execute("SELECT * FROM progress WHERE student_id=?", (student_id_value,))

# Pick this up from login activity
student_info_id = 0 # Guest profile, default
student_info_id = 3 # student with transfer credit
student_info_id = 1 # new student

#student_name = q.user.name

student_progress_query = 'SELECT * FROM student_progress WHERE student_info_id={}'.format(student_info_id)
##program_id = 10
#
##c.execute(complete_records_query, (program_id,))
#df2 = pd.read_sql_query(complete_records_query, conn, params=(program_id,))

# reading student progress directly into pandas
#df_raw = pd.read_sql_query(student_progress_query, conn)

df2 = pd.read_sql_query(templates.complete_student_records_query, conn, params=(student_info_id,))
df_raw = pd.read_sql_query(templates.complete_student_records_query_old, conn, params=(student_info_id,))

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
#df_raw = df_raw.merge(df2[['description','pre_classes', 'pre_credits']], on='class_id', how='left')

# this is a quick hack for the demo
# need to fix the logic

student_progress_records = df_raw.to_dict('records')
student_records_no_schedule = df2.to_dict('records')

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

###############################################################################


# Now user_details is a dictionary containing the user information
@on('#home')
async def home(q: Q):
    clear_cards(q)  # When routing, drop all the cards except (header, footer, meta).
    add_card(q, 'params', cards.render_debug_card(q, location='d3'))

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

###############################################################################

interview_questions = [
    'Have you ever attended a college or university before?',
    'Are you enrolling full-time or part-time?',
    '[If part-time]: Are you working full-time?',
    '[If part-time & working full-time]: Are you attending evening classes?',
    'Are you in-state, out-of-state, or military?'
]

@on('#student')
@on('student_reset')
async def student(q: Q):
    q.page['sidebar'].value = '#student'

    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    add_card(q, 'student_section', ui.form_card(
        box='vertical',
        items=[
            ui.text('Please answer the following questions to personalize your experience:', 
                size=ui.TextSize.L)
        ]
    ))

#    add_card(q, 'student_section', ui.section_card(
#        box='vertical',
#        title='Your title',
#        subtitle='Your subtitle',
#        items=[
#            ui.toggle(name='search', label='Search', value=True),
#            ui.dropdown(name='distribution', label='', value='option0', choices=[
#                ui.choice(name=f'option{i}', label=f'Option {i}') for i in range(5)
#            ]),
#            ui.date_picker(name='target_date', label='', value='2020-12-25'),
#        ],
#    )    

    # If first time on this page, create the card.
    add_card(q, 'form', 
        ui.form_card(
            box='vertical', 
            items=[
                ui.stepper(name='stepper', 
                    items=[
                        ui.step(label='Question 1'),
                        ui.step(label='Question 2'),
                        ui.step(label='Question 3'),
                        ui.step(label='Question 4'),
                        ui.step(label='Question 5'),
                ]),
                ui.textbox(name='textbox1', label=interview_questions[0]),
                ui.buttons(
                    justify='end', 
                    items=[
                        ui.button(name='student_step2', label='Next', primary=True),
                ]),
        ])
    )
    add_card(q, 'student_questions', ui.wide_info_card(
        box=ui.box('grid', width='300px'), 
        name='', 
        icon='AccountActivity',
        title='Questions',
        caption='Appropriate questions will be asked here to help profile student. These are TBD.'
    ))
    add_card(q, 'student_guest', ui.wide_info_card(
        box=ui.box('grid', width='300px'), 
        name='', 
        icon='Contact',
        title='Guest Mode',
        caption='If not logged in, user can explore in Guest mode. We will add the ability to download results for later use.'
    ))
    add_card(q, 'student_login', ui.wide_info_card(
        box=ui.box('grid', width='300px'), 
        name='', 
        icon='ContactLock',
        title='Logged In',
        caption='Student information will be saved for future use.'
    ))
    add_card(q, 'student_api', ui.wide_info_card(
        box=ui.box('grid', width='300px'), 
        name='', 
        icon='Import',
        title='Import',
        caption='Student information can be imported from available data sources. Student will be allowed to update information for this tool.'
    ))

@on()
async def student_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Question 1', done=True),
            ui.step(label='Question 2'),
            ui.step(label='Question 3'),
            ui.step(label='Question 4'),
            ui.step(label='Question 5'),
        ]),
        ui.textbox(name='textbox2', label=interview_questions[1]),
        ui.buttons(justify='end', items=[
            ui.button(name='student_step3', label='Next', primary=True),
        ])
    ]

@on()
async def student_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Question 1', done=True),
            ui.step(label='Question 2', done=True),
            ui.step(label='Question 3'),
            ui.step(label='Question 4'),
            ui.step(label='Question 5'),
        ]),
        ui.textbox(name='textbox3', label=interview_questions[2]),
        ui.buttons(justify='end', items=[
            ui.button(name='student_step4', label='Next', primary=True),
        ])
    ]

@on()
async def student_step4(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Question 1', done=True),
            ui.step(label='Question 2', done=True),
            ui.step(label='Question 3', done=True),
            ui.step(label='Question 4'),
            ui.step(label='Question 5'),
        ]),
        ui.textbox(name='textbox4', label=interview_questions[3]),
        ui.buttons(justify='end', items=[
            ui.button(name='student_step5', label='Next', primary=True),
        ])
    ]

@on()
async def student_step5(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Question 1', done=True),
            ui.step(label='Question 2', done=True),
            ui.step(label='Question 3', done=True),
            ui.step(label='Question 4', done=True),
            ui.step(label='Question 5'),
        ]),
        ui.textbox(name='textbox5', label=interview_questions[4]),
        ui.buttons(justify='end', items=[
            ui.button(name='student_reset', label='Finish', primary=True),
        ])
    ]

###############################################################################


@on('#major')
async def major(q: Q):
    clear_cards(q)
    #add_card(q, 'title3',
    #    ui.form_card(
    #        box=ui.box('top_vertical'),
    #        items=[ui.text('Browse Majors', size=ui.TextSize.XL),
    #]))
    add_card(q, 'dropdown_menus_vertical', cards.dropdown_menus_vertical(q, location='top_horizontal'))
    add_card(q, 'major_recommendations', cards.major_recommendation_card)

    career_url = 'https://www.careeronestop.org/Toolkit/Careers/interest-assessment.aspx'
    add_card(q, 'major_section', ui.form_card(
        box=ui.box('top_horizontal', width='400px'),
        items=[
            ui.text(
                f'**Don\'t know what you want to do?** Take an Interest Assessment sponsored by the U.S. Department of Labor at <a href="{career_url}" target="_blank">CareerOneStop</a>.',
                #size=ui.TextSize.L
            ),
            ui.separator(),
            ui.text('*Can be replaced with UMGC Interest Assessment if one exists*')
          ]
    ))

    program_id = 10
    await cards.render_majors_discovery(q, program_id)
    #query = '''
    #    SELECT b.name || ' in ' || a.name as degree_program
    #    FROM programs a, degrees b
    #    WHERE a.id = ? AND a.degree_id = b.id
    #'''
    #q.app.c.execute(query, (program_id,))
    #q_result = q.app.c.fetchone()
    #if q_result is not None:
    #    title = q_result[0]
    #else:
    #    title = None
#
    #query = '''
    #    SELECT
    #        id,
    #        course,
    #        course_type AS type,
    #        course_type_id,
    #        title,
    #        credits,
    #        description,
    #        pre,
    #        pre_credits,
    #        substitutions
    #    FROM program_requirements_view
    #    WHERE program_requirements_id = (
    #        SELECT id FROM program_requirements WHERE program_id = ?
    #    )
    #'''
    #df = pd.read_sql_query(query, q.app.conn, params=(program_id,))
    #major_records = df.to_dict('records')
    #
    #query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    #df = pd.read_sql_query(query, q.app.conn, params=(program_id,))
    #rows = df.to_dict('records')
    #row = rows[0]
    #
    #await cards.render_major_dashboard(q, title, row, 'middle_vertical')
    #await cards.render_major_table(q, major_records, 'bottom_vertical')


                    #add_card(q, 'dropdown_menus_vertical2', cards.dropdown_menus_vertical(q, location='middle_horizontal'))
    #add_card(q, 'dropdown_menus_vertical3', cards.dropdown_menus_vertical(q, location='middle_horizontal'))


#    new_image_path, = await q.site.upload(['images/program_overview_bmgt.png'])
#    add_card(q, 'example_program_template', ui.image_card(
#        box=ui.box('d3', height='600px', width='80%'),
##        box=ui.box('vertical', width='100%', height='400px'), 
#        type='png',
#        title="Bachelor's in Business Administration Program Overview",
#        #caption='Lorem ipsum dolor sit amet consectetur adipisicing elit.',
#        #category='Category',
#        #label='Click me',
#        #image='https://images.pexels.com/photos/3225517/pexels-photo-3225517.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260',
#        path=new_image_path,
#    ))



###############################################################################

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

table_height = '400px'

complete_records_query = '''
    SELECT 
        a.seq,
        a.name,
        a.program_id,
        a.class_id,
        a.course_type_id,
        b.title,
        b.description,
        b.prerequisites
    FROM 
        program_sequence a
    JOIN 
        classes b
    ON 
        a.class_id = b.id
    WHERE 
        a.program_id = ?
'''
program_id = 10
#c.execute(complete_records_query, (program_id,))
#df2 = pd.read_sql_query(complete_records_query, conn, params=(program_id,))

# change to q.user later
#q.client.degree_program = 'BS in Business Administration'

# generate automatically from form inputs

degree_program = 'BS in Business Administration'
#degree_program = q.user.degree_program
@on('#courses')
async def courses(q: Q):
    clear_cards(q)  
    add_card(q, 'selected_major', 
        ui.form_card(
            box='top_vertical',
            items=[ui.text(degree_program, size=ui.TextSize.XL)]
    ))

# get results from querying database
    add_card(q, 'major_dashboard', ui.form_card(box='top_vertical', items=[
        ui.stats(
#            justify='between', 
            items=[
                ui.stat(
                    label='Total Credits', 
                    value=str(total_credits_remaining), 
                    caption='Total Credits Remaining', 
                    icon='Education'),   
                ui.stat(
                    label='Major Credits', 
                    value=str(33), 
                    caption='Major Credits Remaining', 
                    icon='Trackers'),   
                ui.stat(
                    label='Required Credits', 
                    value=str(12), 
                    caption='Required Credits Remaining', 
                    icon='News'),   
                ui.stat(
                    label='GE Credits', 
                    value=str(41), 
                    caption='General Education Credits Remaining', 
                    icon='TestBeaker'),   
                ui.stat(
                    label='Elective Credits', 
                    value=str(46), 
                    caption='Elective Credits Remaining', 
                    icon='Media'),   
            ]
    )]))

    # automatically group by term?
    # see https://wave.h2o.ai/docs/examples/table-groups

    cards.render_course_table2(q, student_records_no_schedule,
                               title='BS in Business Administration',
                               location='bottom_vertical')

#    cards.render_course_table(q, student_records_no_schedule,
#        which=['MAJOR'],
#        title='Required Major Core Courses (33)',
#        location='middle_horizontal',
#        table_width='48%'
#    )
#    cards.render_course_table(q, student_records_no_schedule, 
#        which=['REQUIRED'], 
#        title='Required Related Courses (12)', 
#        location='middle_horizontal',
#        table_width='48%'
#    )
#    cards.render_ge_table(q, student_records_no_schedule, 
#        #which=['GENERAL'], 
#        #title='Select General Education Courses', 
#        location='middle_horizontal2',
#        table_width='48%'
#    )
#    cards.render_elective_table(q, student_records_no_schedule, 
#        #which=['ELECTIVE'], 
#        #title='Select Elective Courses', 
#        location='middle_horizontal2',
#        table_width='48%'
#    )

    add_card(q, 'ge_tile', 
        ui.wide_info_card(
            box=ui.box('grid', width='400px'), 
            name='', 
            title='Explore General Education',
            caption='Explore and select GE courses'
    ))
    add_card(q, 'electives_tile', 
        ui.wide_info_card(
            box=ui.box('grid', width='400px'), 
            name='', 
            title='Explore Electives',
            caption='Explore and perhaps recommend electives',
    ))
    add_card(q, 'minors_tile', 
        ui.wide_info_card(
            box=ui.box('grid', width='400px'), 
            name='', 
            title='Explore Minors',
            caption='Explore and perhaps recommend minors',
    ))

###############################################################################

# first query: WRTG 111 or another course

#templates.ge_query_j(params=1)

ge_query_j = '''
    SELECT 
        b.id,
        b.name,
        b.title,
        b.credits,
        b.description,
        b.pre,
        b.pre_credits
    FROM 
        general_education a
    LEFT JOIN 
        classes b
    ON 
        a.course_id = b.id
    WHERE 
        b.general_education_requirements_id = ?
'''


@on('#ge')
async def ge(q: Q):
    clear_cards(q)
    add_card(q, 'ge_tile',
        ui.wide_info_card(
            box=ui.box('grid', width='50%'),
            name='',
            title='Explore General Education',
            caption='Explore and select GE courses'
    ))
    cards.render_ge_table(q, student_records_no_schedule,
        #which=['GENERAL'],
        #title='Select General Education Courses',
        location='middle_horizontal',
        table_width='95%'
    )


###############################################################################

@on('#electives')
async def electives(q: Q):
    clear_cards(q)
    add_card(q, 'careers', 
        ui.frame_card(
            box=ui.box('grid', width='100%', height='600px'),
            title='Interest Assessment',
            path='https://www.careeronestop.org/Toolkit/Careers/interest-assessment.aspx',
        )
    )

###############################################################################

@on('#schedule')
async def schedule(q: Q):
    clear_cards(q)  

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
    )]))
    add_card(q, 'd3plot', cards.d3plot(html_template, 'd3'))
    
    Sessions = ['Session 1', 'Session 2', 'Session 3']
    add_card(q, 'sessions_spin', 
        ui.form_card(
            box=ui.box('d3', width='300px'), # min width 200px
            items=[
                ui.dropdown(
                    name='first_term', 
                    label='First Term', 
                    value=q.args.first_term,
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
                    values=['Session 1', 'Session 3'], # set default
                ),
                ui.spinbox(
                    name='spinbox', 
                    label='Courses per Session', 
                    width='150px',
                    min=1, max=5, step=1, value=2),
#                ui.separator(label=''),
                ui.slider(name='slider', label='Max Credits per Term', min=1, max=16, step=1, value=12),
                ui.inline(items=[
                    ui.button(name='show_inputs', label='Submit', primary=True),
                    ui.button(name='reset_sidebar', label='Reset', primary=False),
                ])
            ]
        )
    )

    # automatically group by term?
    # see https://wave.h2o.ai/docs/examples/table-groups
    add_card(q, 'course_table', ui.form_card(box='bottom_vertical', items=[
        ui.table(
            name='table',
            downloadable=True,
            resettable=True,
            groupable=True,
            columns=[
                #ui.table_column(name='seq', label='Seq', data_type='number'),
                ui.table_column(
                    name='course', 
                    label='Course', 
                    searchable=True, 
                    sortable=True,
                    min_width='50', # check this
                    max_width='100', #check this
                    link=True
                ),
                ui.table_column(
                    name='title', 
                    label='Title', 
                    searchable=True, 
                    min_width='100', # check this
                    max_width='200', 
                    cell_overflow='wrap'
                ),
                #ui.table_column(name='description', label='Description', searchable=True, max_width='200',
                #    #cell_overflow='tooltip', 
                #    cell_overflow='wrap', 
                #    #cell_type=ui.markdown_table_cell_type(target='_blank'),
                #    ),
                ui.table_column(name='credits', label='Credits', data_type='number', max_width='50', align='center'),
                cards.render_tag_column('150'),
                ui.table_column(name='term', label='Term', filterable=True, max_width='120'),
                ui.table_column(
                    name='session', 
                    label='Session', 
                    data_type='number', 
                    max_width='80', # check this
                    align='center'),
                ui.table_column(
                    name='actions', 
                    label='Menu', 
                    max_width='100', 
                    align='left',
                    cell_type=ui.menu_table_cell_type(
                        name='commands', 
                        commands=[
                            ui.command(name='reschedule', label='Move Class'),
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
                    record['title'],
                    #record['description'],
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

###############################################################################


###############################################################################

###############################################################################

async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()

async def initialize_app(q: Q):
    """
    Initialize the app.
    """
    logging.info('Initializing app')

    q.app.umgc_logo, = await q.site.upload(['images/umgc-logo.png'])
    q.app.conn = sqlite3.connect('UMGC.db')
    q.app.c = q.app.conn.cursor()
    q.app.ge_total = 41 # total ge credits
    q.app.initialized = True

async def initialize_user(q: Q) -> None:
    """
    Initialize the app.
    """
    logging.info('Initializing user')

    keycloak_implemented = False
    # temporary until keycloak login fully implemented
#    if keycloak_implemented:
        # Decode the access token without verifying the signature
        # Connects SSO to our user and student_info tables
#        user_details = jwt.decode(q.auth.access_token, options={"verify_signature": False})

#        q.user.username = user_details['preferred_username']
#        q.user.name = user_details['name']
#        q.user.firstname = user_details['given_name']
#        q.user.lastname = user_details['family_name']

        # check whether user is in the sqlite3 db
        # if so, get role and id
        # if not, add user to db as a new student
#        q.user.user_id, q.user.role_id = utils.find_or_add_user(q)
#    else:
#        # fake it for now
    q.user.username = 'johndoe'
    q.user.name = 'John Doe'
    q.user.firstname = 'John'
    q.user.lastname = 'Doe'
    q.user.user_id = 1
    q.user.role_id = 1


    # if a student, get information from the student_info table
    query = ''' 
        SELECT resident_status_id, transfer_credits, financial_aid, stage, program_id, profile, notes
        FROM student_info WHERE user_id = ?
    '''
    if q.user.role_id == 1:
        q.user.student = True
        q.app.c.execute(query, (q.user.user_id,))
        row = q.app.c.fetchone()
        if row is not None:
            (q.user.resident_status_id, q.user.transfer_credits, q.user.financial_aid, q.user.stage, q.user.program_id,
             q.user.profile, q.user.notes) = row

    q.user.initialized = True

async def initialize_client(q: Q) -> None:
    q.page['meta'] = cards.meta
    q.page['header'] = cards.get_header(q.app.umgc_logo, q)
    q.page['footer'] = cards.footer

    # If no active hash present, render home.
    if q.args['#'] is None:
        await home(q)

#async def show_error(q: Q, error: str):
#    """
#    Displays errors.
#    """
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

## need to fix so broadcast and multicast work correctly

@app('/', mode='unicast', on_startup=on_startup)
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """
    try:

        if not q.app.initialized:
            await initialize_app(q)

        if not q.user.initialized:
            await initialize_user(q)

        # Run only once per client (browser tab) connection.
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


# close the sqlite3 connection 
conn.close()