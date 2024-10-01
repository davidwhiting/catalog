## This file should contain cards but generally not place them.
## Thus, cards are either defined by a function (because they have to access Q)
## or they are an object themselves.

from h2o_wave import Q, ui, main, app, run_on, on, data, copy_expando, expando_to_dict, graphics as g
from typing import Optional, List
import logging
import traceback
import sys
import json
import pandas as pd
import numpy as np

from backend.queries import degree_query, area_query, program_query, program_query_old
from backend.queries import ge_query, ge_pairs_query, ge_credits_query 
from backend.student import get_choices
from frontend.utils import add_card, clear_cards
import frontend.constants as constants
from backend.connection import TimedSQLiteConnection

#import templates_13

######################################################
####################  HOME CARDS  ####################
######################################################

def return_task1_card(location='top_horizontal', width='350px'):
    '''
    Task 1 Card repeated on home page and home/1, home/2, etc.
    '''
    task_1_caption = f'''
### Enter selected information 
- Residency status
- Attendance type
- Financial aid
- Transfer credits
'''
    card = ui.wide_info_card(
        box=ui.box(location, width=width),
        name='task1',
        icon='AccountActivity',
        title='Task 1',
        caption=task_1_caption
    )
    return card

def return_demographics_card(location='top_horizontal', width='400px') -> ui.FormCard:
    '''
    Demographics card for home page
    '''
    attendance_choices = [
        ui.choice('full-time', 'Full Time'),
        ui.choice('part-time', 'Part Time'),
        ui.choice('evening', 'Evening only'),
    ]
    card = ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.text_xl('Tell us about yourself'),
            ui.text('This information will help us build a course schedule'),
            ui.inline(items=[
                ui.choice_group(name='attendance', label='I will be attending', choices=attendance_choices, required=True),
            ]),
            ui.separator(name='my_separator', width='100%', visible=True),
            ui.checkbox(name='financial_aid', label='I will be using Financial Aid'),
            ui.checkbox(name='transfer_credits', label='I have credits to transfer'),
            ui.button(name='next_home', label='Next', primary=True),
        ]
    )
    return card


def return_tasks_card(checked=0, location='top_horizontal', width='350px', height='400px'):
    '''
    Return tasks optionally checked off
    '''
    icons = ['Checkbox', 'Checkbox', 'Checkbox', 'Checkbox']
    checked_icon = 'CheckboxComposite'
    # checked needs to be a value between 0 and 4
    if checked > 0:
        for i in range(checked):
            icons[i] = checked_icon

    card = ui.form_card(
        box=ui.box(location, width=width, height=height),
        items=[
            #ui.text(title + ': Credits', size=ui.TextSize.L),
            ui.text('Task Tracker', size=ui.TextSize.L),
            ui.stats(items=[ui.stat(
                label=' ',
                value='1. Information',
                caption='Tell us about yourself',
                icon=icons[0],
                icon_color='#135f96'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='2. Select Program',
                caption='Decide what you want to study',
                icon=icons[1],
                icon_color='#a30606'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='3. Add Courses',
                caption='Add GE and Electives',
                icon=icons[2],
                #icon_color='#787800'
                icon_color='#3c3c43'
            )]),
            ui.stats(items=[ui.stat(
                label=' ',
                value='4. Create Schedule',
                caption='Optimize your schedule',
                icon=icons[3],
                icon_color='#da1a32'
            )]),
        ])
    return card

def return_program_selection_card(location='horizontal', width='60%'):
    """
    Create the program selection card
    """
    card = ui.form_card(
        box=ui.box(location, width=width),
        #name='program_selection',
        #title='Select a UMGC Program',
        #caption='Choose an option to explore UMGC programs',
        #category='Program Selection',
        #icon='Education',
        items=[
            ui.text_xl(content='**Select a UMGC Program**'),
            ui.link(label='Option 1: Explore programs on your own', path='/#program'),
            ui.link(label='Option 2: Select a program based on your skills', path='/#skills'),
            ui.link(label='Option 3: Select a program based on your interests', disabled=True),
            ui.link(label='Option 4: Select a program that finished your degree the quickest', disabled=True)
        ]
    )
    return card


##########################################################
####################  PROGRAMS CARDS  ####################
##########################################################

async def render_dropdown_menus_horizontal(q, location='horizontal', menu_width='300px'):
    '''
    Create menus for selecting degree, area of study, and program
    '''
    si = q.client.student_info
    conn = q.client.conn    
    enabled_degree = {"Bachelor's", "Undergraduate Certificate"}
    disabled_programs = q.app.disabled_program_menu_items

    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(si['menu']['degree']) if (si['menu']['degree'] is not None) \
                else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices = await get_choices(conn, degree_query, disabled=None, enabled=enabled_degree)
        ),
        ui.dropdown(
            name='menu_area',
            label='Area of Study',
            value=str(si['menu']['area_of_study']) if (str(si['menu']['area_of_study']) is not None) \
                else str(q.args.menu_area),
            trigger=True,
            disabled=False,
            width='250px',
            choices=None if (si['menu']['degree'] is None) else \
                await get_choices(conn, area_query, params=(si['menu']['degree'],))
        ),
        ui.dropdown(
            name='menu_program',
            label='Program',
            value=str(si['menu']['program']) if \
                (si['menu']['program'] is not None) else q.args.menu_program,
            trigger=True,
            disabled=False,
            width='300px',
            choices=None if (si['menu']['area_of_study'] is None) else \
                await get_choices(conn, program_query, params=(si['menu']['degree'], si['menu']['area_of_study']),
                    disabled=disabled_programs
                )
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='select_program', label='Select Program'),
            #ui.command(name='classes_menu', label='Classes', 
            #    items=[
            #        ui.command(name='add_ge', label='Add GE'),
            #        ui.command(name='add_elective', label='Add Electives'),  
            #]),
            ui.command(name='add_ge', label='Add GE'),
            ui.command(name='add_elective', label='Add Electives')  
    ])

    card = ui.form_card(
        box = location,
        items = [
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
    add_card(q, 'dropdown', card)

async def render_dropdown_skills_menu(q, location='horizontal', menu_width='300px'):
    '''
    Create menus for selecting program based on skills survey
    '''
    si = q.client.student_info
    conn = q.client.conn    
    #enabled_degree = {"Bachelor's", "Undergraduate Certificate"}
    disabled_programs = q.app.disabled_program_menu_items

    # enforcing string because I've got a bug somewhere (passing an int instead of str)
    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_skills_program',
            label='Program',
            value=str(si['menu']['program']) if \
                (si['menu']['program'] is not None) else q.args.menu_skills_program,
            trigger=True,
            disabled=False,
            width='300px',
            choices=None if (si['menu']['area_of_study'] is None) else \
                await get_choices(conn, program_query, params=(si['menu']['degree'], si['menu']['area_of_study']),
                    disabled=disabled_programs
                )
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='select_program', label='Select Program'),
            #ui.command(name='classes_menu', label='Classes', 
            #    items=[
            #        ui.command(name='add_ge', label='Add GE'),
            #        ui.command(name='add_elective', label='Add Electives'),  
            #]),
            #ui.command(name='add_ge', label='Add GE'),
            #ui.command(name='add_elective', label='Add Electives')  
    ])

    card = ui.form_card(
        box = location,
        items = [
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
    add_card(q, 'dropdown', card)


async def return_program_description_card(conn: TimedSQLiteConnection, student_info: dict, 
        location: str = 'top_vertical', width: str = '100%', height: str = '100px') -> ui.MarkdownCard:
    '''
    Returns the program description in an card
    :param location: page location to display
    '''
    title = student_info['degree_program'] # program name
    box = ui.box(location, width=width, height=height)
    query = '''
        SELECT description, info, learn, certification
        FROM program_descriptions WHERE program_id = ?
    '''
    row = await conn.query_one(query, params=(student_info['program_id'],))
    if row:
        # major = '\n##' + title + '\n\n'
        frontstuff = "\n\n#### What You'll Learn\nThrough your coursework, you will learn how to\n"
        if int(student_info['program_id']) in (4, 24, 29):
            content = row['info'] + '\n\n' + row['description']
        else:
            content = row['description'] + frontstuff + row['learn'] #+ '\n\n' + row['certification']

        card = ui.markdown_card(
            box=box, 
            title=title,
            content=content
        )
        return card
    else:
        return None

async def return_program_dashboard_card(conn: TimedSQLiteConnection, student_info: dict, location: str = 'horizontal', width: str = '100px') -> ui.FormCard:
    '''
    Returns the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    title = student_info['degree_program'] # program name

    box = ui.box(location, width=width)
    #if student_info['menu_degree'] == '2':

    # get program summary for bachelor's degrees
    query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    row = await conn.query_one(query, params=(student_info['program_id'],))
    if row:
        card = ui.form_card(
            box=box,
            items=[
                #ui.text(title + ': Credits', size=ui.TextSize.L),
                ui.text('Credits', size=ui.TextSize.L),
                ui.stats(items=[ui.stat(
                    label='Major',
                    value=str(row['major']),
                    #caption='Credits',
                    icon='Trackers',
                    icon_color='#135f96'
                )]),
                ui.stats(items=[ui.stat(
                    label='Required Related',
                    value=str(row['related_ge'] + row['related_elective']),
                    #caption='Credits',
                    icon='News',
                    icon_color='#a30606'
                )]),
                ui.stats(items=[ui.stat(
                    label='General Education',
                    value=str(row['remaining_ge']),
                    #caption='Remaining GE',
                    icon='TestBeaker',
                    #icon_color='#787800'
                    icon_color='#3c3c43'
                )]),
                ui.stats(items=[ui.stat(
                    label='Elective',
                    value=str(row['remaining_elective']),
                    #caption='Remaining Elective',
                    icon='Media',
                    icon_color='#fdbf38'
                )]),
                ui.separator(),
                ui.stats(items=[ui.stat(
                    label='TOTAL',
                    value=str(row['total']),
                    #caption='Remaining Elective',
                    icon='Education',
                    icon_color='#da1a32 '
                )]),
        ])
        return card
    else:
        return None

async def render_program_table(q: Q, location: str = 'horizontal', width: str = '90%', 
                               height: str = '500px', check: bool = True, ge: bool = False, elective: bool = False):
    '''
    q:
    df:
    location:
    cardname:
    width:
    height:
    ge: Include GE classes
    elective: Include Elective classes
    '''
    student_data = q.client.student_data
    df = student_data['required']

    async def _render_program_group(group_name, record_type, df, collapsed, check=True):
        '''
        group_name: 
        record_type: 
        df: course (Pandas) dataframe
        collapsed:
        check: If True, only return card if # rows > 0
            e.g., we will always return 'MAJOR' but not necessarily 'REQUIRED'
        '''
        # card will be returned if 
        # (1) check == False
        # (2) check == True and sum(rows) > 0
        no_rows = ((df['type'].str.upper() == record_type).sum() == 0)

        if check and no_rows: #(check and not_blank) or (not check):
            return ''
        else:
            return ui.table_group(group_name, [
                ui.table_row(
                    #name=str(row['id']),
                    name=row['course'],
                    cells=[
                        row['course'],
                        row['title'],
                        str(row['credits']),
                        row['type'].upper(),
                    ]
                ) for _, row in df.iterrows() if row['type'].upper() == record_type
            ], collapsed=collapsed)

    # Create groups with logic
    groups = []
    result = await _render_program_group(
        'Required Major Core Courses',
        'MAJOR',
        df, collapsed=False, check=False
    )
    if result != '':
        groups.append(result)
    logging.info('MAJOR')

    result = await _render_program_group(
        'Required Related Courses/General Education',
        'REQUIRED,GENERAL',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)
    logging.info('REQUIRED,GENERAL')
    
    result = await _render_program_group(
        'Required Related Courses/Electives',
        'REQUIRED,ELECTIVE',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)
    logging.info('REQUIRED,ELECTIVE')

    if ge:
        result = await _render_program_group(
            'General Education',
            'GENERAL',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)
        
    if elective:
        result = await _render_program_group(
            'Electives',
            'ELECTIVE',
            df, collapsed=True, check=False
        )
        if result != '':
            groups.append(result)

    columns = [
        # ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300',
                        cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=constants.UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_program_description', label='Course Description'),
                    #ui.command(name='prerequisites', label='Show Prerequisites'),
                ]
        ))
    ]

    box = ui.box(location, height=height, width=width)

    #title = q.client.student_info['degree_program'] + ': Explore Required Courses'
    title = 'Explore Required Courses'

    card = ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='describe_program', label='About', 
                    #caption='Description', 
                    primary=True, disabled=True)
            ]),
            ui.table(
                name='program_table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height=height,
                columns=columns,
                groups=groups
            )
        ]
    )
    add_card(q, 'program_table_card', card)

async def render_program_description_card(q: Q, location='top_vertical', width='100%', height='100px') -> None:
    '''
    Renders the program description in an article card
    :param q: instance of Q for wave query
    :param location: page location to display
    '''
    conn = q.client.conn
    student_info = q.client.student_info
    card = await return_program_description_card(conn, student_info, location=location, width=width, height=height)
    add_card(q, 'program_description', card)

async def render_program_dashboard_card(q, location='horizontal', width='100px'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    conn = q.client.conn
    student_info = q.client.student_info
    card = await return_program_dashboard_card(conn, student_info, location=location, width=width)

    if card:
        add_card(q, 'major_dashboard', card)

async def render_program_cards(q: Q):
    await render_program_description_card(q, location='top_vertical', height='200px', width='100%')
    await render_program_table(q, location='horizontal', width='90%')
    await render_program_dashboard_card(q, location='horizontal', width='150px')

#############################################################
####################  SKILLS CARDS ##########################
#############################################################

async def return_skills_menu_card(conn: TimedSQLiteConnection, defaults=None, location='vertical', width='300px', height='800px',inline=False):
    '''
    Create skills choice menu
    Will send the selected skills to the database query and return a list of courses
    '''
    #query = 'SELECT id AS name, name AS label, explanation AS tooltip FROM Skills'
    query = 'SELECT id AS name, name AS label FROM Skills'

    #choices = await backend.get_choices_new(timed_connection, skills_query, disabled={""}, tooltip=False)
    choices = await get_choices(conn, query, disabled={""})

    card = ui.form_card(
        box = ui.box(location, width=width, height=height),
        items=[
            #                ui.separator(),
            ui.checklist(
                name='skills_checklist',
                label='Skills',
                #value=str(si['menu']['program']) if (si['menu']['program'] is not None) else q.args.menu_program,
                values=defaults,
                inline=inline,
                choices = choices,
            ),
            #ui.number(name='result_limit', label='Number of results', min=5, max=15, step=1, value=7),
            #ui.inline(items=[
            ui.button(name='submit_skills_menu', label='Submit', primary=True),
            ui.button(name='reset_skills_menu', label='Reset', primary=False),
            #])
        ]
    )
    return card

async def return_skills_table(results, location='horizontal'):
    """
    Return the skills table given input of results from get_query_dict
    Called by submit_skills_menu
    """
    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='program', label='Program', searchable=False, min_width='250'),
        ui.table_column(name='score', label='Score', searchable=False, min_width='100'), 
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='explore_skills_program', label='Explore Program'),
                    ui.command(name='select_skills_program', label='Select Program'),
                ]
        ))
    ]
    rows = [
        ui.table_row(
            name=str(row['id']),
            #name=row['program'],
            cells=[
                #str(row['seq']),
                row['program'],
                #str(row['TotalScore']),
                f"{row['TotalScore']:.3f}"
            ]
        ) for row in results
    ]
    card = ui.form_card(
        box=ui.box(location),
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='program_skills_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                columns=columns,
                rows=rows
            )
        ]
    )
    return card

#########################################################
####################  COURSES CARDS  ####################
#########################################################

async def render_course_page_table_use(q, box=None, location='vertical', width=None, height=None, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    data: a list of dictionaries, each element corresponding to a row of the table 
    location:
    cardname:
    width:
    height:
    '''

    df = q.client.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=constants.UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='select_elective', label='Select Elective'),
                ]
        ))
        #ui.table_column(name='menu', label='Menu', max_width='150',
        #    cell_type=ui.menu_table_cell_type(name='commands', 
        #        commands=[
        #            ui.command(name='view_description', label='Course Description'),
        #            ui.command(name='show_prereq', label='Show Prerequisites'),
        #            ui.command(name='select_elective', label='Select Elective'),
        #        ]
        #))
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
            ]
        ) for _, row in df.iterrows()
    ]

    box = ui.box(location, height=height, width=width)
    degree_program = q.client.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            ui.inline(justify='between', align='center', items=[
                ui.text(title, size=ui.TextSize.L),
                ui.button(name='schedule_coursework', label='Schedule', 
                    #caption='Description', 
                    primary=True, disabled=False)
            ]),
            ui.table(
                name='course_table',
                downloadable=False,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    #return card


####################################################
####################  GE CARDS  ####################
####################################################

def ge_debug_content(q):
    result = f'''
### q.client.student_info['ge'] values:

- Arts: {q.client.student_info['ge']['arts']}
- Beh: {q.client.student_info['ge']['beh']}
- Bio: {q.client.student_info['ge']['bio']}
- Comm: {q.client.student_info['ge']['comm']}
- Math: {q.client.student_info['ge']['math']}
- Res: {q.client.student_info['ge']['res']}

### q.args values:
{q.args}

### q.events values:
{q.events}

#### q.page['ge_bio']
{dir(q.page['ge_bio'])}

{ q.page['ge_bio'].items['ge_bio_1a'].value }

#### Whole GE
{q.client.student_info['ge']}

### q.client value:
{q.client}
'''
    return result


async def render_ge_arts_card(q, menu_width='300px', location='grid', 
                              cardname='ge_arts', width='300px'):
    '''
    Create the General Education - Arts card
    '''
    ge = q.client.student_info['ge']['arts']
    nopre = ge['nopre']
    conn = q.client.conn
    box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Arts and Humanities', size=ui.TextSize.L),
                ui.checkbox(name='ge_arts_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_arts_1',
                label='1. Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(conn, ge_query, (7,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_beh_card(q, menu_width='300px', location='grid', 
                             cardname='ge_beh', width='300px'):
    '''
    Create the General Education - Behavioral and Social Sciences card
    '''
    ge = q.client.student_info['ge']['beh']
    nopre = ge['nopre']
    conn = q.client.conn
    box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            #ui.separator(label=''),
            ui.inline([
                ui.text('Behavioral and Social Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_beh_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_beh_1',
                label='1. Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_beh_1,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (12,))
                #choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_beh_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (13,))
#                choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (11,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_bio_card(q, menu_width='300px', location='grid', 
                             cardname='ge_bio', width='300px'):
    '''
    Create the General Education - Science card
    '''
    conn = q.client.conn
    ge = q.client.student_info['ge']['bio']
    nopre = ge['nopre']
    box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Biological and Physical Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_bio_check', label='')
            ], justify='between', align='start'),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            #ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='1. Lecture & Lab (4 credits): Select one',
                value = ge['1a'] if (ge['1a'] is not None) else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Combined Lecture & Lab)',
                required=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (8,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                #label='Separate Lecture and Laboratory',
                value=ge['1c'] if (ge['1c'] is not None) else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Separate Lecture & Lab)',
                width=menu_width,
                #choices=await utils.get_choices_disable_all(conn, ge_pairs_query, ())
                choices=await get_choices(conn, ge_pairs_query, ())
            ),
            ui.dropdown(
                name='ge_bio_1b',
                #label='For Science Majors and Minors only:',
                value=ge['1b'] if (ge['1b'] is not None) else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Science Majors and Minors)',
                width=menu_width,
                choices=await get_choices(conn, ge_query, (9,))
            ),
            #ui.separator(label='Select an additional science course:'),
            #nopre=True # check for easy classes by selecting those w/o prerequisites
            ui.dropdown(
                name='ge_bio_2',
                label='2. An additional course (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_bio_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
#                choices=await get_choices(timedConnection, ge_query_nopre if nopre else ge_query, (10,))
                choices=await get_choices(conn, ge_query, (11,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_comm_card(q, menu_width='300px', location='grid', 
                             cardname='ge_comm', width='300px'):
    '''
    Create the General Education - Communications card
    '''
    conn = q.client.conn
    ge = q.client.student_info['ge']['comm']
    nopre = ge['nopre']
    box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Communications', size=ui.TextSize.L),
                ui.checkbox(name='ge_comm_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_comm_1',
                label='1. WRTG 111 or equivalent (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_comm_1,
                trigger=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_2',
                label='2. WRTG 112 (3 credits)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_comm_2,
                disabled=False,
                trigger=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_3',
                label='3. Another course (3 credits)',
                placeholder='(Select One)',
                value=ge['3'] if (ge['3'] is not None) else q.args.ge_comm_3,
                trigger=True,
                popup='always',
                required=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_4',
                label='4. Advanced writing course (3 credits)',
                placeholder='(Select One)',
                value=ge['4'] if (ge['4'] is not None) else q.args.ge_comm_4,
                trigger=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (4,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_math_card(q, menu_width='300px', location='grid', 
                             cardname='ge_math', width='300px'):
    '''
    Create the General Education - Mathematics card
    '''
    ge = q.client.student_info['ge']['math']
    conn = q.client.conn
    nopre = ge['nopre']
    box = ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Mathematics', size=ui.TextSize.L),
                ui.checkbox(name='ge_math_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_math_1',
                label='One Course (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(conn, ge_query, (5,))
            ),
        ]
    )
    add_card(q, cardname, card)

async def render_ge_res_card(q, menu_width='300px', location='grid', 
                             cardname='ge_res', width='300px'):
    '''
    Create the General Education - Research and Computing Literacy card
    '''
    conn = q.client.conn
    ge = q.client.student_info['ge']['res']
    nopre = ge['nopre']
    box = ui.box(location, width=width)
    # make some defaults based on area of program chosen:
    if q.client.student_info['menu']['area_of_study'] == '1':
        ge['1'] = 'PACE 111B'
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Research and Computing Literacy', size=ui.TextSize.L),
                ui.checkbox(name='ge_res_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_res_1',
                label='1. Professional Exploration (3 credits)',
                value=ge['1'] if (ge['1'] is not None) else q.args.ge_res_1,
                # default value will depend on the major chosen
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(conn, ge_query, (14,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills / Professional Development (1 credit)',
                value=ge['2'] if (ge['2'] is not None) else q.args.ge_res_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(conn, ge_query, (15,))
            ),
            ui.dropdown(
                name='ge_res_3',
                label='3. Computing or IT (3 credits)',
                value=ge['3'] if (ge['3'] is not None) else q.args.ge_res_3,
                trigger=True,
                required=True,
                placeholder='(Select 3-credit Course)',
                width=menu_width,
                choices=await get_choices(conn, ge_credits_query, (16,3))
            ),
           ui.dropdown(
                name='ge_res_3a',
                label='[or three 1-credit courses]:',
                required=True,
                value=ge['3a'] if (ge['3a'] is not None) else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(conn, ge_credits_query, (16,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                #label='Computing or Information Technology (1 credit)',
                value=ge['3b'] if (ge['3b'] is not None) else q.args.ge_res_3b,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(conn, ge_credits_query, (16,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                #label='Computing or Information Technology (1 credit each)',
                value=ge['3c'] if (ge['3c'] is not None) else q.args.ge_res_3c,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(conn, ge_credits_query, (16,1))
            ),
        ]
    )
    add_card(q, cardname, card)

##########################################################
####################  SCHEDULE CARDS  ####################
##########################################################

def render_elective_cards(q):
    caption = '''

### 1. Select electives with no prerequisites
### 2. Add a Foreign Language sequence (multiple electives)
### 3. Add a Minor (multiple electives selected)
### 4. Suggest electives based on skills and interests
### 5. Suggest electives that are popular (low difficulty?)

'''
    card = ui.wide_info_card(
        box=ui.box('horizontal', width='700px'),
            name='elective1',
            icon='AccountActivity',
            title='Elective Methods to be Implemented',
            caption=caption
    )
    add_card(q, 'elective1', card)

##########################################################
####################  SCHEDULE CARDS  ####################
##########################################################

async def render_schedule_page_table(q, box=None, location='horizontal', width='90%', height=None):
    '''
    Input comes from 
    q:
    location:
    cardname:
    width:
    height:
    '''
    df = q.client.student_data['schedule']

    def _get_commands(course, type):
        # for creating adaptive menus
        # to complete later
        if course == 'ELECTIVE':
            commands = [ui.command(name='select_elective', label='Select Elective')]
        elif course == 'GENERAL':
            commands = [ui.command(name='select_general', label='Select GE Course')]
        else:
            commands = [
                ui.command(name='view_schedule_description', label='Course Description'),
            ]
            if type in ['ELECTIVE', 'GENERAL']:
                commands.append(ui.command(name='change_course', label='Change Course'))

        return commands

    columns = [
        #ui.table_column(name='seq', label='Seq', data_type='number'),
        ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
        ui.table_column(name='title', label='Title', searchable=False, min_width='180', 
                        max_width='300', cell_overflow='wrap'),
        ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                        align='center'),
        ui.table_column(
            name='tag',
            label='Type',
            min_width='190',
            filterable=True,
            cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=constants.UMGC_tags
            )
        ),
        ui.table_column(name='term', label='Term', max_width='50', data_type='number'),        
        ui.table_column(name='session', label='Session', max_width='80', data_type='number'),
        ui.table_column(name='locked', label='Locked', max_width='50', data_type='number'),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_schedule_description', label='Course Description'),
                    ui.command(name='move_class', label='Move Class'),
                    ui.command(name='lock_class', label='Lock/Unlock Class'),
                ]
        ))
        #            ui.command(name='select_elective', label='Select Elective'),
    ]
    rows = [
        ui.table_row(
            #name=str(row['id']),
            name=row['name'],
            cells=[
                #str(row['seq']),
                row['name'],
                row['title'],
                str(row['credits']),
                row['course_type'].upper(),
                str(row['term']),
                str(row['session']),
                str(row['locked']),
            ]
        ) for _, row in df.iterrows()
    ]

    box = ui.box(location, width=width)

    degree_program = q.client.student_info['degree_program']
    title = f'**{degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'schedule_table', ui.form_card(
        box=box,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
            ui.table(
                name='schedule_table',
                downloadable=True,
                resettable=True,
                groupable=False,
                height=height,
                columns=columns,
                rows=rows
            )
        ]
    ))
    return card

async def return_d3plot(q, html, location='horizontal', 
                        height='500px', width='100%', add_title=False):
    '''
    Create the D3 display from html input
    '''
    box=ui.box(location, height=height, width=width)
    title = 'Course Schedule' if add_title else ''

    card = ui.frame_card(
        box=box,
        title=title,
        content=html
    )
    return card

async def render_d3plot(q, html, location='horizontal', height='500px', 
                        width='100%', cardname='schedule/d3_display', add_title=False):
    '''
    Create the D3 display from html input
    '''
    card = await return_d3plot(q, html, location, height, width, add_title)
    add_card(q, cardname, card)

async def return_schedule_menu(q, location='vertical', width='300px'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.client.student_info fields)
    '''

    Sessions = ['Session 1', 'Session 2', 'Session 3']
    default_attend_summer = True
    student_profile = q.client.student_info['student_profile']
    if student_profile == 'Full-time':
        ## full-time: 
        ##   - 14 week and 17 week terms: (min 12, max 18)
        ##   - 4 week term: (min 3, max 6)
        ## half-time:
        ##   - 14 week and 17 week terms: (min 6)

        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 15
        default_courses_per_session = 2
    elif student_profile == 'Part-time':
        # todo: get courses_per_session and max_credits from university rules
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 7
        default_courses_per_session = 1
    else:
        # todo: enumerate the rest of the profile cases
        default_sessions = ['Session 1', 'Session 3']
        default_max_credits = 13
        default_courses_per_session = 2

    card = ui.form_card(
        box = ui.box(location, width=width),
        items=[
            ui.dropdown(
                name='first_term',
                label='First Term',
                value=q.client.student_info['first_term'] if (q.client.student_info['first_term'] is not None) \
                    else q.args.first_term,
                trigger=False,
                width='150px',
                # todo: create these choices via same function call as used in scheduling slots
                choices=[
                    ui.choice(name='Spring 2024', label="Spring 2024"),
                    ui.choice(name='Summer 2024', label="Summer 2024"),
                    ui.choice(name='Fall 2024', label="Fall 2024"),
                    ui.choice(name='Winter 2025', label="Winter 2025"),
                ]),
            #                ui.separator(),
            ui.checklist(
                name='sessions_checklist',
                label='Sessions Attending',
                choices=[ui.choice(name=x, label=x) for x in Sessions],
                values=default_sessions,  # set default
            ),
            ui.spinbox(
                name='courses_per_session',
                label='Courses per Session',
                width='150px',
                min=1, max=5, step=1, value=default_courses_per_session),
            #                ui.separator(label=''),
            ui.slider(name='max_credits', label='Max Credits per Term', min=1, max=18, 
                step=1, value=default_max_credits),
            ui.checkbox(name='attend_summer', label='Attending Summer', 
                value=default_attend_summer),
            ui.inline(items=[
                ui.button(name='submit_schedule_menu', label='Submit', primary=True),
                ui.button(name='reset_schedule_menu', label='Reset', primary=False),
            ])
            #ui.button(name='submit_schedule_menu', label='Submit', primary=True),
        ]
    )
    return card

async def render_schedule_menu(q, location='horizontal', width='300px',
                               cardname='schedule/menu'):
    '''
    Create menu for schedule page
    (retrieve defaults from DB or from q.client.student_info fields)
    '''
    card = await return_schedule_menu(q, location=location, width=width )
    add_card(q, cardname, card)


def generate_header_data(start_semester, num_periods, data_df):

    # Constants
    HEADER_WIDTH = 260
    SUMMER_HEADER_WIDTH = 190
    HEADER_OFFSET = 3
    SUMMER_HEADER_OFFSET = 2

    X_GAP = 40
    X_OFFSET = 10
    Y_GAP = 4
    Y_OFFSET = 10
    SESSION_OFFSET = 70
    HEADER_ROW = 20    

    seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
    semester_data = []
    start_season, start_year = start_semester.split(' ')
    start_year = int(start_year)
    season_index = seasons.index(start_season)
    year = start_year
    period = 0

    while period < num_periods:
        for j in range(season_index, len(seasons)):
            semester_data.append(f'{seasons[j]} {year}')
            period += 1

            # Break the loop when i equals num_periods
            if period == num_periods:
                break

        # Reset the season index to start from 'WINTER' for the next year
        season_index = 0
        year += 1

    df = pd.DataFrame(semester_data, columns=['term'])
    df['width'] = df['term'].apply(lambda x: SUMMER_HEADER_WIDTH if 'SUMMER' in x else HEADER_WIDTH)
    df['offset'] = df['term'].apply(lambda x: SUMMER_HEADER_OFFSET if 'SUMMER' in x else HEADER_OFFSET)
    df['fontsize'] = '14px'
    df['description'] = ''
    df['space'] = X_GAP
    df['xpos'] = df['width'] + df['space']

    x0 = 10
    # Calculate the cumulative sum of 'xpos'
    df['x'] = df['xpos'].cumsum()
    df['x'] = df['x'].shift(1)
    df.loc[0, 'x'] = 0
    df['x'] = df['x'] + X_OFFSET
    df['y'] = Y_OFFSET
    df['color'] = 'lightgray'
    df['textcolor'] = 'black'
    df['period'] = np.arange(1, num_periods+1)

    df.drop
    # Sum credits per period and convert to a DataFrame
    total_credits = data_df.groupby('period')['credits'].sum().sort_index()
    total_credits_df = total_credits.reset_index()

    df = pd.merge(df, total_credits_df, on='period', how='inner')
    df['name'] = df['term']
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'

    # quick fix for period needed here

    return df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 
               'fontsize', 'period', 'name', 'credits', 'description']]

def prepare_d3_data(df, start_term='SPRING 2024'):
    '''
    Prepare data for input into D3 figure
    Note: Uses 'period' instead of 'term'
    '''
    # Use UMGC Colors
    green = '#3b8132'
    blue = '#135f96'
    red = '#a30606'
    yellow = '#fdbf38'
    def _set_colors(row):
        if row['type'] == 'general':
            return pd.Series([green, 'white'])
        elif row['type'] == 'major':
            return pd.Series([blue, 'white'])
        # hack: fix the following 3 elifs
        elif row['type'] == 'required,elective':
            row['type'] = 'required'
            return pd.Series([red, 'white'])
        elif row['type'] == 'required,general':
            row['type'] = 'required'
            return pd.Series([red, 'white'])
        elif row['type'] == 'required':
            return pd.Series([red, 'white'])
        elif row['type'] == 'elective':
            return pd.Series([yellow, 'black'])
        else:
            return pd.Series(['white', 'black'])  # default colors

    def _generate_header_data(start_semester, num_periods, data_df = df):
        seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
        semester_data = []
        start_season, start_year = start_semester.split(' ')
        start_year = int(start_year)
        season_index = seasons.index(start_season)
        year = start_year
        period = 0

        while period < num_periods:
            for j in range(season_index, len(seasons)):
                semester_data.append(f'{seasons[j]} {year}')
                period += 1

                # Break the loop when i equals num_periods
                if period == num_periods:
                    break

            # Reset the season index to start from 'WINTER' for the next year
            season_index = 0
            year += 1

        df = pd.DataFrame(semester_data, columns=['term'])
        df['width'] = df['term'].apply(lambda x: 190 if 'SUMMER' in x else 260)
        df['offset'] = df['term'].apply(lambda x: 2 if 'SUMMER' in x else 3)
        df['fontsize'] = '14px'
        df['description'] = ''
        df['space'] = 40
        df['xpos'] = df['width'] + df['space']

        x0 = 10
        # Calculate the cumulative sum of 'xpos'
        df['x'] = df['xpos'].cumsum()
        df['x'] = df['x'].shift(1)
        df.loc[0, 'x'] = 0
        df['x'] = df['x'] + x0
        df['y'] = 10
        df['color'] = 'lightgray'
        df['textcolor'] = 'black'
        df['period'] = np.arange(1, num_periods+1)

        df.drop
        # Sum credits per period and convert to a DataFrame
        total_credits = data_df.groupby('period')['credits'].sum().sort_index()
        total_credits_df = total_credits.reset_index()

        df = pd.merge(df, total_credits_df, on='period', how='inner')
        df['name'] = df['term']
        df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'

        return df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 
                   'fontsize', 'period', 'name', 'credits', 'description']]

    # Prepare data for the D3 figure

    max_period = max(df['period'])
    headers = _generate_header_data(start_term, max_period)

    df['description'] = df['prerequisites']
    df['width'] = 120
    # Calculate 'x' column
    df = pd.merge(df, headers[['period','x']], on='period', how='left')
    df['x'] += 70*(df['session']-1)

    # Calculate 'y' column
    df = df.sort_values(by=['period', 'session', 'seq' ])
    df['y_row'] = df.groupby('period').cumcount() + 1
    df['y'] = 70 + 45 * (df['y_row'] - 1)

    # Create rectangle colors
    df[['color', 'textcolor']] = df.apply(_set_colors, axis=1)

    # Set text offset multiplier to 1 and text fontsize
    df['offset'] = 1
    df['fontsize'] = '12px'
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'
    
    df = df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 'fontsize', 'period', 'session', 'type', 'name', 'credits', 'description']]

    return df, headers

## Note: Escape curly brackets {} with {{}} so that substitution within Python works properly

def create_html_template(df, start_term):
    '''
    Function that takes the q.user.student_data['schedule'] dataframe 
    and converts it to the html_template to create the Javascript D3 figure
    '''
    # accept start_term both as 'spring2024' and 'Spring 2024'. Make sure to
    # return as the latter
    if ' ' in start_term:
        term = start_term.upper()
    else:
        season = start_term[:-4]
        year = start_term[-4:]
        term = f"{season.upper()} {year}"

    # rename because the function uses 'period' rather than 'term'
    # to do: inefficient, need to rewrite
    df_input = df.copy()
    df_input.rename(columns={'term': 'period'}, inplace=True)

    df_display, headers_display = prepare_d3_data(df_input, term)
    df_json = df_display.to_json(orient='records')
    headers_json = headers_display.to_json(orient='records')

    html_template = constants.html_minimal_template.format(
        javascript=constants.javascript_draw_only,
        headers=headers_json, 
        data=df_json)
    
    return html_template

#######################################################
####################  DEBUG CARDS  ####################
#######################################################

async def return_debug_card(q, location='debug', width='100%', height='300px'):
    '''
    Show q.client information in a card for debugging
    '''
    #expando_dict = expando_to_dict(q.client)
    #q_client_filtered = {k: v for k, v in expando_dict.items() if k not in ['student_info', 'student_data']}

    #### q.client.student_data values:
    #{q.client.student_data}
    box = ui.box(location, width=width, height=height)

    content2 = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.app values:
{q.app}

### q.user values:
{q.user}

### q.client value:
{q.client}

### q.client.student_info values:
{q.client.student_info}

### q.client.student_data values:
{q.client.student_data}

#### Required:
{q.client.student_data['required']}

#### Schedule:
{q.client.student_data['schedule']}

### remaining q.client values:
{q_client_filtered}

    '''
    content3 = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.app values:
{q.app}

### q.user values:
{q.user}

### q.client value:
{q.client}

'''
    content = f'''
### q.client values:
{q.client}

'''

    card = ui.markdown_card(
        box,
        title='Debug Information', 
        content=content 
    )
    return card

########################################################
####################  LAYOUT CARDS  ####################
########################################################

def sidebar_card(q: Q, home: str = '#home') -> ui.NavCard:
    '''
    Sidebar for navigation
    '''
    return ui.nav_card(
        box='sidebar', 
        color='primary', 
        title='UMGC', 
        subtitle='Registration Assistant',
        value=f'#{q.args["#"]}' if q.args['#'] else home,
        image=q.app.logo, 
        items=[
            ui.nav_group('1. Student Info', items=[
                ui.nav_item(name='#home', label='Home'),
            ]),
            ui.nav_group('2. Select Program', items=[
                #ui.nav_item(name='#program_group', label='Program'),
                ui.nav_item(name='#program', label='→ Explore'),
                ui.nav_item(name='#skills', label='→ Skills')
            ]),
            ui.nav_group('3. Add Courses', items=[
                ui.nav_item(name='#courses', label='Required'),
                ui.nav_item(name='#ge', label='→ GE'),
                ui.nav_item(name='#electives', label='→ Electives'),
            ]),
            ui.nav_group('4. Create Schedule', items=[
                ui.nav_item(name='#schedule', label='Schedule'),
            ]),
        ]
    )

header_card = ui.header_card(
    box='header', 
    #title='UMGC Registration Assistant', 
    title='Registration Assistant', 
    subtitle='',
    #subtitle="Registration Assistant",
    #title='', subtitle='',
    #secondary_items=[
        #ui.textbox(name='search', icon='Search', width='400px', placeholder='Search...'),
    #],
    items=[
        ui.persona(title='John Doe', subtitle='Student', size='xs',
            image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
    ]
)

footer_card = ui.footer_card(
    box='footer',
    caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
'''
)

def return_meta_card() -> ui.MetaCard:
    '''
    Function to return the meta card for the UMGC app.
    Includes customizations for UMGC.
    '''
    title='UMGC Wave App'
    theme_name='UMGC'
    UMGC_themes=[ui.theme( # UMGC red: '#a30606', UMGC yellow: '#fdbf38'
        name='UMGC',
        primary='#a30606', 
        text='#000000',
        card='#ffffff',
        page='#e2e2e2', 
    )]
    body_zones = [
        ui.zone('header'),
        ui.zone('content', zones=[
            ## Specify various zones and use the one that is currently needed. Empty zones are ignored.
            ## Usually will not need the top_ or bottom_ versions
            ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
            ui.zone('top_vertical'),
            ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
            ui.zone('vertical'),
            ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'),
            #ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
            #ui.zone('bottom_vertical'),
            ui.zone('debug', direction=ui.ZoneDirection.ROW)
        ]),
        ui.zone('footer')
    ]
    UMGC_layouts=[ui.layout(
        breakpoint='xs', min_height='100vh', 
        zones=[
            ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, 
                zones=[
                    ui.zone('sidebar', size='200px'),
                    ui.zone('body', zones=body_zones),
                ]
            )
        ]
    )]
    card = ui.meta_card(
        box = '',
        themes = UMGC_themes,
        theme = theme_name,
        title = title,
        layouts = UMGC_layouts
    )
    return card 

meta_card = return_meta_card()

#################################################################
####################  CARDS FOR BUG HANDLING ####################
#################################################################

from frontend.constants import APP_NAME as app_name
from frontend.constants import REPO_URL as repo_url
from frontend.constants import ISSUE_URL as issue_url

# A fallback card for handling bugs
fallback_card = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

def crash_report_card(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
    This function is called by the main serve() loop on uncaught exceptions.
    """

    def code_block(content): 
        return '\n'.join(['```', *content, '```'])

    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)

    dump = [
        '### Stack Trace',
        code_block(stack_trace),
    ]

    states = [
        ('q.app', q.app),
        ('q.user', q.user),
        ('q.client', q.client),
        ('q.events', q.events),
        ('q.args', q.args)
    ]
    for name, source in states:
        dump.append(f'### {name}')
        dump.append(code_block([f'{k}: {v}' for k, v in expando_to_dict(source).items()]))

    return ui.form_card(
        box='error',
        items=[
            ui.stats(
                items=[
                    ui.stat(
                        label='',
                        value='Oops!',
                        caption='Something went wrong',
                        icon='Error'
                    )
                ],
            ),
            ui.separator(),
            ui.text_l(content='Apologies for the inconvenience!'),
            ui.buttons(items=[ui.button(name='reload', label='Reload', primary=True)]),
            ui.expander(name='report', label='Error Details', items=[
                ui.text(
                    f'To report this issue, <a href="{issue_url}" target="_blank">please open an issue</a> with the details below:'),
                ui.text_l(content=f'Report Issue in App: **{app_name}**'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )
