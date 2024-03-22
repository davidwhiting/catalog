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
# utils contains all other python functions
import utils

from utils import add_card, single_query, query_row

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
#need to make this await
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
    javascript=templates.javascript_draw_only,
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

#home_tabs = [
#    ui.tab(name='email', label='Mail', icon='Mail'),
#    ui.tab(name='events', label='Events', icon='Calendar'),
#    ui.tab(name='spam', label='Spam'),
#]

#def get_tab_content(category: str):
#    # Return a checklist of dummy items.
#    items = [f'{category.title()} {i}' for i in range(1, 11)]
#    return ui.checklist(name='items', choices=[ui.choice(name=item, label=item) for item in items])

###############################################################################
@on('#home')
async def home(q: Q):
    clear_cards(q)  # When routing, drop all the cards except (header, footer, meta).
    await cards.render_home_cards(q)

    #rao_card = cards.rao_table(location='middle_horizontal')
    #add_card(q, name='rao_table', rao_card)

    # Database
    # UI
    # Wave
    # Code
    # Data


    card = await cards.render_project_table(templates.project_data)
    add_card(q, 'project_table_location', card)

    ## Debug Information
    add_card(q, 'params', cards.render_debug_card(q, location='d3'))

###############################################################################

@on('#student')
@on('student_reset')
async def student(q: Q):
    q.page['sidebar'].value = '#student'

    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    add_card(q, 'student_section', ui.form_card(
        box='middle_vertical',
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
            box='middle_vertical',
            items=[
                ui.stepper(name='stepper', 
                    items=[
                        ui.step(label='Question 1'),
                        ui.step(label='Question 2'),
                        ui.step(label='Question 3'),
                        ui.step(label='Question 4'),
                        ui.step(label='Question 5'),
                ]),
                ui.textbox(name='textbox1', label=cards.interview_questions[0]),
                ui.buttons(
                    justify='end', 
                    items=[
                        ui.button(name='student_step2', label='Next', primary=True),
                ]),
        ])
    )
    #career_url = 'https://www.careeronestop.org/Toolkit/Careers/interest-assessment.aspx'
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'

    add_card(q, 'assessments', ui.wide_info_card(
        box=ui.box('bottom_horizontal', width='400px'),
        name='Assessments',
        icon='AccountActivity',
        title='Career Assessments',
        caption=f'Access career assessment tools like **UMGC CareerQuest** or add a page like <a href="{yale_url}" target="_blank">Yale\'s</a> with _Interest_, _Personality_, and _Skills_ assessments.',
    ))
    add_card(q, 'enable_ai', ui.wide_info_card(
        box=ui.box('bottom_horizontal', width='300px'),
        name='ai',
        icon='LightningBolt',
        title='AI Enablement',
        caption='*Interest* or *Skills* assessments critical for AI recommendations.'
    ))

    #add_card(q, 'student_api', ui.wide_info_card(
    #    box=ui.box('grid', width='300px'),
    #    name='',
    #    icon='Import',
    #    title='Import',
    #    caption='Student information can be imported from available data sources. Student will be allowed to update information for this tool.'
    #))
    #add_card(q, 'skills_assessment', ui.wide_info_card(
    #    box=ui.box('grid', width='600px'),
    #    name='',
    #    icon='AccountActivity',
    #    title='Skills Assessment',
    #    caption=f'**Don\'t know what you want to do?** Take an Interest Assessment sponsored by the U.S. Department of Labor at <a href="{career_url}" target="_blank">CareerOneStop</a>.',
    #))

    #add_card(q, 'student_questions_old', ui.wide_info_card(
    #    box=ui.box('grid', width='300px'),
    #    name='',
    #    icon='AccountActivity',
    #    title='Questions',
    #    caption='Appropriate questions will be asked here to help profile student. These are TBD.'
    #))

    #add_card(q, 'student_login', ui.wide_info_card(
    #    box=ui.box('grid', width='300px'),
    #    name='',
    #    icon='ContactLock',
    #    title='Logged In',
    #    caption='Student information will be saved for future use.'
    #))

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
        ui.textbox(name='textbox2', label=cards.interview_questions[1]),
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
        ui.textbox(name='textbox3', label=cards.interview_questions[2]),
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
        ui.textbox(name='textbox4', label=cards.interview_questions[3]),
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
        ui.textbox(name='textbox5', label=cards.interview_questions[4]),
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
    add_card(q, 'major_recommendations', cards.major_recommendation_card)
    add_card(q, 'dropdown_menus_vertical', cards.dropdown_menus_vertical(q, location='top_horizontal'))

    #career_url = 'https://www.careeronestop.org/Toolkit/Careers/interest-assessment.aspx'
    #add_card(q, 'major_section', ui.form_card(
    #    box=ui.box('top_horizontal', width='400px'),
    #    items=[
    #        ui.text(
    #            f'**Don\'t know what you want to do?** Take an Interest Assessment sponsored by the U.S. Department of Labor at <a href="{career_url}" target="_blank">CareerOneStop</a>.',
    #            #size=ui.TextSize.L
    #        ),
    #        ui.separator(),
    #        ui.text('*Can be replaced with UMGC Interest Assessment if one exists*')
    #      ]
    #))

    # the program id should be returned from the menu
    program_id = 10

    await cards.render_majors_discovery(q, program_id)

###############################################################################

@on('#major2')
async def major2(q: Q):
    clear_cards(q)
    #add_card(q, 'title3',
    #    ui.form_card(
    #        box=ui.box('top_vertical'),
    #        items=[ui.text('Browse Majors', size=ui.TextSize.XL),
    #]))
    add_card(q, 'major_recommendations', cards.major_recommendation_card)
    add_card(q, 'dropdown_menus_vertical', cards.dropdown_menus_vertical(q, location='top_horizontal'))
    add_card(q, 'dropdown_menus_vertical2', cards.dropdown_menus_vertical_compare(q, location='top_horizontal'))

    #career_url = 'https://www.careeronestop.org/Toolkit/Careers/interest-assessment.aspx'
    #add_card(q, 'major_section', ui.form_card(
    #    box=ui.box('top_horizontal', width='400px'),
    #    items=[
    #        ui.text(
    #            f'**Don\'t know what you want to do?** Take an Interest Assessment sponsored by the U.S. Department of Labor at <a href="{career_url}" target="_blank">CareerOneStop</a>.',
    #            #size=ui.TextSize.L
    #        ),
    #        ui.separator(),
    #        ui.text('*Can be replaced with UMGC Interest Assessment if one exists*')
    #      ]
    #))

    # the program id should be returned from the menu
    program_id = 10

    await cards.render_majors_discovery(q, 2)
    #await cards.render_majors_discovery(q, 10, compare=True)

###############################################################################

@on('#courses')
async def courses(q: Q):
    clear_cards(q)

    # temp, move to appropriate spot
    q.user.degree_program = 'BS in Business Administration'
    #q.user.program_id

    add_card(q, 'selected_major', 
        ui.form_card(
            box='top_vertical',
            items=[ui.text(q.user.degree_program, size=ui.TextSize.XL)]
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
                               title=q.user.degree_program,
                               location='middle_vertical')

#    cards.render_course_table(q, student_records_no_schedule,
#        which=['MAJOR'],
#        title='Required Major Core Courses (33)',
#        location='middle_horizontal',
#        table_width='48%'
#    )
#    cards.render_course_table(q, student_records_no_schedule, 
#        which=['REQUIRED'], 
#        title='Required Related Courses (12)', 
#        location='bottom_horizontal',
#        table_width='48%'
#    )
#    cards.render_ge_table(q, student_records_no_schedule, 
#        #which=['GENERAL'], 
#        #title='Select General Education Courses', 
#        location='bottom_horizontal',
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
            box=ui.box('grid', width='300px'),
            name='', 
            title='Explore General Education',
            caption='Explore and select GE courses'
    ))
    add_card(q, 'electives_tile', 
        ui.wide_info_card(
            box=ui.box('grid', width='300px'),
            name='', 
            title='Explore Electives',
            caption='Explore and perhaps recommend electives',
    ))
    add_card(q, 'minors_tile', 
        ui.wide_info_card(
            box=ui.box('grid', width='300px'),
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
    add_card(q, 'selected_major',
        ui.form_card(
            box='top_horizontal',
            items=[
                ui.text(#q.user.degree_program,
                    'BS in Business Administration',
                    size=ui.TextSize.XL
    )]))
    #add_card(q, 'more_student_info',
    #    ui.form_card(
    #        box='top_horizontal',
    #        items=[
    #            ui.separator(label='John Doe Profile:'),
    #            ui.text('Military Tuition'),
    #            ui.text('Evening School'),
    #        ]
    #))

    add_card(q, 'd3plot', cards.d3plot(html_template, 'd3'))

    demo = True
    Sessions = ['Session 1', 'Session 2', 'Session 3']
    add_card(q, 'sessions_spin', 
        ui.form_card(
            box=ui.box('d3', width='300px'), # min width 200px
            items=[
                ui.dropdown(
                    name='first_term', 
                    label='First Term', 
                    value='spring2024' if demo else q.args.first_term,
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
                    values=['Session 1', 'Session 2', 'Session 3'], # set default
                ),
                ui.spinbox(
                    name='spinbox', 
                    label='Courses per Session', 
                    width='150px',
                    min=1, max=5, step=1, value=1),
#                ui.separator(label=''),
                ui.slider(name='slider', label='Max Credits per Term', min=1, max=16, step=1, value=9),
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

@on('#progress_chart')
async def progress_chart(q: Q):
    clear_cards(q)
    add_card(q, 'careers',
        ui.frame_card(
            box=ui.box('grid', width='100%', height='600px'),
            title='Interest Assessment',
            path='https://www.careeronestop.org/Toolkit/Careers/interest-assessment.aspx',
        )
    )

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

    q.app.umgc_logo, = await q.site.upload(['images/umgc-logo-white.png'])
    q.app.conn = sqlite3.connect('UMGC.db')
    q.app.c = q.app.conn.cursor()
    q.app.ge_total = 41 # total ge credits

    q.app.start_term = 'Spring 2024'

    q.app.initialized = True


async def initialize_user(q: Q) -> None:
    """
    Initialize the app.
    """
    logging.info('Initializing user')

    keycloak_implemented = False
    ##### KEYCLOAK CODE ##############
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

    ## That works for the entire website, not for an individual login
    ## See https://docs.h2o.ai/mlops/py-client/py-client-examples/keycloak-authentication-methods
    ##### KEYCLOAK CODE ##############

    q.user.user_id = 1

    # Get user information
    query = '''
        SELECT role_id, username, firstname, lastname, 
            firstname || ' ' || lastname AS name
        FROM users
        WHERE id = ?
    '''
    row = query_row(query, (q.user.user_id,), q.app.c)
    (q.user.role_id, q.user.username, q.user.firstname, q.user.lastname, q.user.name) = row

    # If a student, get information from the student_info table
    query = ''' 
        SELECT resident_status_id, transfer_credits, financial_aid, stage, program_id, profile, notes
        FROM student_info WHERE user_id = ?
    '''
    if q.user.role_id == 1:
        q.user.student = True
        row = query_row(query, (q.user.user_id,), q.app.c)
        (q.user.resident_status_id, q.user.transfer_credits, q.user.financial_aid, q.user.stage, q.user.program_id,
         q.user.profile, q.user.notes) = row


    # End of student information

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

    #@app('/demo')
    #async def serve(q: Q):
        #await q.page.save()

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

    #if q.args.home_menu:
    #    q.page['home'].items = [
    #        ui.tabs(name='home_menu', value=q.args.menu, items=home_tabs),
    #        get_tab_content(q.args.menu),
    #    ]
    #else:
    #    q.page['home'] = ui.form_card(box='middle_horizontal', items=[
    #        ui.tabs(name='home_menu', value='email', items=home_tabs),
    #        get_tab_content('email'),
    #    ])

    # Handle routing.
    await run_on(q)
    await q.page.save()


# close the sqlite3 connection 
conn.close()