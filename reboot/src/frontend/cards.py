## This file should contain cards but generally not place them.
## Thus, cards are either defined by a function (because they have to access Q)
## or they are an object themselves.

from h2o_wave import Q, ui, main, app, run_on, on, data, copy_expando, expando_to_dict
from typing import Optional, List
import logging
import traceback
import sys


from backend.queries import degree_query, area_query, program_query, program_query_old 
from backend.student import get_choices
from frontend.utils import add_card, clear_cards
import frontend.constants
from backend.connection import TimedSQLiteConnection

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
            ui.button(name='next_demographic_1', label='Next', primary=True),
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
                tags=frontend.constants.UMGC_tags
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
    logging.info('render_program_description_card')
    await render_program_table(q, location='horizontal', width='90%')
    logging.info('render_program_table')
    await render_program_dashboard_card(q, location='horizontal', width='150px')
    logging.info('render_program_dashboard_card')

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
        #current_page = q.args["#"] if q.args['#'] else 'page1',
        #value=f'#{current_page}',
        image=q.app.logo, 
        items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#home', label='Home'),
                ui.nav_item(name='#program', label='Program'),
                ui.nav_item(name='#explore', label='→ Explore'),
                ui.nav_item(name='#skills', label='→ Skills'),
                ui.nav_item(name='#courses', label='Courses'),
                ui.nav_item(name='#ge', label='→ GE'),
                ui.nav_item(name='#electives', label='→ Electives'),
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
            #ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
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
