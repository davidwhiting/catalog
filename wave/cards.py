from h2o_wave import ui
from typing import Optional, List
import utils
from utils import get_query, get_query_one
import pandas as pd
import sys

######################################################################
####################  STANDARD WAVE CARDS (START) ####################
######################################################################

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)

def render_meta_card(flex=False):
    title='UMGC Wave App'
    theme_name='UMGC'
    UMGC_layouts=[ui.layout(
        breakpoint='xs', 
        #min_height='100vh', 
        zones=[
            # size='0' keeps zone from expanding
            ui.zone('header', size='80px'), 
            ui.zone('content', zones=[
                # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
                ui.zone('top_vertical'),
                ui.zone('middle_horizontal', direction=ui.ZoneDirection.ROW),
                ui.zone('middle_vertical'),
                ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'), # delete eventually
                ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
                ui.zone('bottom_vertical'),
                ui.zone('debug', direction=ui.ZoneDirection.ROW), 
            ], size='100%-80px'),
            ui.zone('footer', size='0'),
        ]
    )]
    UMGC_themes=[ui.theme( # UMGC red: '#a30606', UMGC yellow: '#fdbf38'
        name='UMGC',
        primary='#a30606', 
        text='#000000',
        card='#ffffff',
        page='#e2e2e2', 
    )]
    if flex:
        # card with layouts
        card = ui.meta_card(
            box='', themes=UMGC_themes, theme=theme_name, title=title,
            layouts=UMGC_layouts,
        )
    else:
        card = ui.meta_card(
            box='', themes=UMGC_themes, theme=theme_name, title=title,
        )
    return card 

   #############
    ## Testing ##
    #############
    #q.user.user_id = 0 # guest
    #q.user.user_id = 1 # admin
    #q.user.user_id = 2 # counselor
    q.user.user_id = 3 # John Doe, student
    #q.user.user_id = 4 # Jane Doe, transfer student
    #q.user.user_id = 5 # Jim Doe, new student no major selected
    #q.user.user_id = 6 # Sgt Doe, military and evening student

def render_header(q, box='1 1 7 1', flex=False):
    '''
    flex: Use the old flex layout system rather than the grid system
          (flex was not working correctly, can debug later)
    '''
    if flex:
        box='header'
    card = ui.header_card(
        box=box, 
        title='UMGC', 
        subtitle='Registration Assistant',
        image=q.app.umgc_logo,
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                #ui.tab(name='#student', label='Student Info'),
                ui.tab(name='#major', label='Program'), # 'Select Program'
                ui.tab(name='#course', label='Course'), # 'Select Courses'
                #ui.tab(name='#ge', label='GE'), # 'Select Courses'
                #ui.tab(name='#electives', label='Electives'), # 'Select Courses'
                ui.tab(name='#schedule', label='Schedule'), # 'Set Schedule'
                ui.tab(name='#project', label='Project'), # 'Project Plan'
            ]),
        ],
        items=[
            ui.textbox(
                name='textbox_default', 
                label='Student Name', 
                value='John Doe', 
                disabled=False
            )
            #ui.dropdown(
            #    name='user_dropdown',
            #    label='Name',
            #    value=str(q.user.user_id) if (q.user.user_id is not None) else q.args.user_dropdown,
            #    trigger=True,
            #    width='200px',
            #    #choices=await get_choices(q, user_query)
            #    choices = [
            #        ui.choice(name=str(0), label='Guest'),
            #        ui.choice(name=str(1), label='Admin'),
            #        ui.choice(name=str(2), label='Counselor'),
            #        ui.choice(name=str(3), label='John Doe'),
            #        ui.choice(name=str(4), label='Jane Doe'),
            #        ui.choice(name=str(5), label='Jim Doe'),
            #        ui.choice(name=str(6), label='Sgt Doe'),
            #    ]
            #)
        ]
    )

    return card

def render_footer(box='1 10 7 1', flex=False):
    '''
    flex: Use the flex layout system rather than the grid system
    '''
    if flex:
        box='footer'
    card = ui.footer_card(
        box=box,
        caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
        '''
    )
    return card

######################################################################
####################  STANDARD WAVE CARDS (END)   ####################
######################################################################

######################################################################
####################  SQL QUERIES & UTILITIES (START) ################
######################################################################

# These are used in app.py and elsewhere
degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
area_query = '''
    SELECT DISTINCT menu_area_id AS name, area_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ?
'''
program_query = '''
    SELECT program_id AS name, program_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''

def render_dialog_description(q, course):
    '''
    Display the description of a row clicked on a table
    '''
    df = q.client.program_df
    description = df.loc[df['course'] == course, 'description'].iloc[0]

    q.page['meta'].dialog = ui.dialog(
        name = 'view_description',
        title = course + ' Course Description',
        width = '480px',
        items = [ui.text(description)],
        closable = True,
        #events = ['dismissed']
    )

async def get_role(q):
    # get role given a user id
    query = '''
        SELECT 
		    a.role_id,
		    b.type AS role,
		    a.username, 
		    a.firstname || ' ' || a.lastname AS fullname
        FROM 
			users a, roles b
		WHERE 
			a.role_id=b.id AND a.id = ?
    '''
    row = await get_query_one(q, query, params=(q.user.user_id,))
    q.user.role_id = row['role_id']
    q.user.role = row['role']
    q.user.username = row['username']
    q.user.name = row['fullname']

async def get_student_info(q, user_id):
    # get information from student_info table
    # create a view for this
    query = '''
        SELECT 
            a.user_id, 
            b.firstname || ' ' || b.lastname AS fullname,
            c.label AS resident_status, 
            a.app_stage_id,
            d.stage as app_stage,
            e.label AS student_profile,
            a.transfer_credits, 
            a.financial_aid,
            a.program_id
        FROM 
            student_info a
        LEFT JOIN
            users b
        ON
            a.user_id = b.id
        LEFT JOIN
            resident_status c
        ON
            a.resident_status_id=c.id
        LEFT JOIN
            app_stage d
        ON
            a.app_stage_id=d.id
        LEFT JOIN
            student_profile e
        ON
            a.student_profile_id=e.id
        WHERE 
            user_id = ?
    '''   
    row = await get_query_one(q, query, params=(user_id,))
    if row:
        q.user.X_resident_status = row['resident_status']
        q.user.X_app_stage_id = row['app_stage_id']
        q.user.X_app_stage = row['app_stage']
        q.user.X_student_profile = row['student_profile']
        q.user.X_financial_aid = row['financial_aid']
        q.user.X_transfer_credits = row['transfer_credits']
        q.user.X_program_id = row['program_id']
        if q.user.X_program_id is not None:
            row = await utils.get_program_title_new(q, q.user.X_program_id)
            if row:
                q.user.X_degree_program = row['title']
                q.user.X_degree_id = row['id']
    
    # retrieve menu status for students
    query = '''
        SELECT menu_degree_id, menu_area_id 
        FROM menu_all_view
        WHERE program_id = ?
        LIMIT 1
    '''
    # limit 1 because there is not a strict 1:1 correspondence between study areas and programs
    row = await get_query_one(q, query, params=(q.user.X_program_id,))
    if row:
        q.user.X_menu_degree = row['menu_degree_id']
        q.user.X_menu_area = row['menu_area_id']

######################################################################
####################  SQL QUERIES & UTILITIES  (END)   ###############
######################################################################

##############################################################
####################  DEBUG CARDS (START) ####################
##############################################################

def render_debug_card_old(q, location='debug', width='33%', height='200px'):
    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

    '''
    return ui.markdown_card(
        box=ui.box(location, width=width, height=height), 
        title='Debugging Information', 
        content=content 
    )

def render_debug_card(q, location='debug', width='33%', height='200px'):
    content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

    '''
    card = ui.markdown_card(
        box=ui.box(location, width=width, height=height), 
        title='Debugging Information', 
        content=content 
    )
    new_card = ui.form_card(
        box=ui.box(location, width=width, height=height),items=[ui.expander(
            name='debug_expander', 
            label='Debug q.args and q.events',
            items=[ui.textbox('Something should appear here')]
        )]
    )
    return card

def render_debug_client_card(q, location='debug', width='33%', height='200px'):
    content = f'''

### q.client value:
{q.client}

    '''
    return ui.markdown_card(
        ui.box(location, width=width, height=height), 
        title='Client Debugging Information', 
        content=content 
    )

def render_debug_user_card(q, flex=False, box='2 2 3 3', location='debug', width='33%', height='200px'):
    if flex:
        box = ui.box(location, width=width, height=height)
    content = f'''

### q.user values:
{q.user}

    '''
    return ui.markdown_card(
        box=box, 
        title='User Debugging Information', 
        content=content 
    )

def render_debug_app_card(q, flex=False, box='2 2 3 3', location='debug', width='33%', height='200px'):
    if flex:
        box = ui.box(location, width=width, height=height)
    content = f'''
### q.app values:
{q.app}

    '''
    return ui.markdown_card(
        box=box, 
        title='App Debugging Information', 
        content=content 
    )

def render_debug(q, location='debug', width='25%', height='230px'):
    add_card(q, 'debug_user_info', render_debug_user_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q,  location=location, width=width, height=height)) 
    add_card(q, 'debug_info', render_debug_card(q, location=location, width=width, height=height)) 

##############################################################
####################  DEBUG CARDS (END)   ####################
##############################################################

##############################################################
####################  HOME PAGE (START)  #####################
##############################################################

def render_welcome_card_old(q, box='1 2 7 1'):
    add_card(q, 'welcome_home', ui.form_card(
        box=box,
        items=[
            ui.text_l('Welcome to the UMGC Registration Assistant'),
            ui.text('We will guide you through this experience.')
        ]
    ))

def render_welcome_card(q, box='1 2 4 1'):
    add_card(q, 'welcome_home', ui.form_card(
        box=box,
        items=[
            ui.text_l('Welcome to the UMGC Registration Assistant'),
            #ui.text('We will guide you through this experience.')
        ]
    ))

def render_please_login(q, box='5 2 3 1'):
    add_card(q, 'please_login', ui.form_card(
        box=box,
        items=[
            ui.text('You are a **Guest**. Login to save your information.'),
            #ui.text('We will guide you through this experience.')
        ]
    ))

def render_welcome_back_card(q, box='1 3 3 3', title=''):
    content = f'''## Welcome back, {q.user.X_name}.

### Here is your current selected information:

- **Selected program**: {q.user.X_degree_program}

- **Residency status**: {q.user.X_resident_status}

- **Student type**: {q.user.X_student_profile}

- **Transfer credits**: {q.user.X_transfer_credits==1}

- **Financial aid**: {q.user.X_financial_aid==1}
'''
    add_card(q, 'user_info',
        ui.markdown_card(
            box=box,
            title=title,
            content=content
        )
    )
    #add_card(q, 'user_info', 
    #    ui.form_card(
    #        box=box,
    #        items=[
    #            content,
    #            ui.inline(
    #                items=[
    #                    ui.button(name='show_recommendations', label='Submit', primary=True),
    #                    ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
    #                ]
    #            )
    #        ]
    #    )
    #)




def render_career_assessment_card(box='1 1 2 2', flex=False, location='bottom_horizontal'):
    if flex:
        box=ui.box(location, width='400px')
    yale_url = 'https://your.yale.edu/work-yale/learn-and-grow/career-development/career-assessment-tools'
    caption=f'Access career assessment tools like **UMGC CareerQuest** or add a page like <a href="{yale_url}" target="_blank">Yale\'s</a> with _Interest_, _Personality_, and _Skills_ assessments.'
    card = ui.wide_info_card(
        box=box,
        name='Assessments',
        icon='AccountActivity',
        title='Career Assessments',
        caption=caption
    )
    return card

def render_ai_enablement_card(box='1 1 2 2', flex=False, location='bottom_horizontal'):
    if flex:
        box=ui.box('bottom_horizontal', width='400px')
    card = ui.wide_info_card(
        box=box,
        name='ai',
        icon='LightningBolt',
        title='AI Enablement',
        caption='*Interest* or *Skills* assessments critical for AI recommendations.'
    )
    return card

##############################################################
####################  HOME PAGE (END)    #####################
##############################################################

##############################################################
####################  PROGRAMS PAGE (START) ##################
##############################################################

async def get_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
    return choices

async def get_choices_with_disabled(q, query, params=()):
    disabled_items = {
        'Cybersecurity Technology',
        'Social Science',
        'Applied Technology',
        'Web and Digital Design',        
        'East Asian Studies',
        'English',
        'General Studies',
        'History'
    }
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label'], \
        disabled=(str(row['label']) in disabled_items)) for row in rows]
    return choices

async def render_dropdown_menus_horizontal(q, box='1 2 6 1', location='top_horizontal', flex=False, menu_width='280px'):
    #degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
    #area_query = '''
    #    SELECT DISTINCT menu_area_id AS name, area_name AS label
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ?
    #'''
    #program_query = '''
    #    SELECT program_id AS name, program_name AS label
    #    FROM menu_all_view 
    #    WHERE menu_degree_id = ? AND menu_area_id = ?
    #'''

    disabled = []

    # enforcing string because I've got a but somewhere (passing an int instead of str)

    dropdowns = ui.inline([
        ui.dropdown(
            name='menu_degree',
            label='Degree',
            value=str(q.user.X_menu_degree) if (q.user.X_menu_degree is not None) else q.args.menu_degree,
            trigger=True,
            width='230px',
            choices=await get_choices(q, degree_query)
        ),
        ui.dropdown(
            name='menu_area',
            label='Area of Study',
            value=str(q.user.X_menu_area) if (str(q.user.X_menu_area) is not None) else \
                str(q.args.menu_area),
            trigger=True,
            disabled=False,
            width='250px',
            choices=None if (q.user.X_menu_degree is None) else \
                await get_choices(q, area_query, (q.user.X_menu_degree,))
        ),
        ui.dropdown(
            name='menu_program',
            label='Program',
            value=str(q.user.X_program_id) if (q.user.X_program_id is not None) else q.args.menu_program,
            trigger=True,
            disabled=False,
            width='300px',
            choices=None if (q.user.X_menu_area is None) else \
                await get_choices_with_disabled(q, program_query, (q.user.X_menu_degree, q.user.X_menu_area))
        )
    ], justify='start', align='start')

    command_button = ui.button(
        name='command_button', 
        label='Select', 
        disabled=False,
        commands=[
            ui.command(name='program', label='Save Program'),
            ui.command(name='classes_menu', label='Classes', 
                items=[
                    ui.command(name='add_ge', label='Add GE'),
                    ui.command(name='add_elective', label='Add Electives'),  
            ])
    ])

    if flex:
        box = location
    else:
        box = box

    card = ui.form_card(box=box,
        items=[
            #ui.text_xl('Browse Programs'),
            ui.inline([
                dropdowns, 
                command_button
            ],
            justify='between', 
            align='end')
        ]
    )
        
    return card

    ########################

def render_major_recommendation_card(q, box='1 5 3 3', flex=False, location='top_horizontal', width='350px'):
    if flex:
        box=ui.box(location, width=width)
    card = ui.form_card(
        box=box,
        items=[
            ui.choice_group(
                name='recommendation_group',
                label='Recommend a major based on ...',
                choices=[
                    ui.choice('A', label='My interests'),
                    ui.choice('B', label='My skills'),
                    ui.choice('C', label='Students like me'),
                    ui.choice('D', label='Shortest time to graduate'),
                ]),
            ui.inline(
                items=[
                    ui.button(name='show_recommendations', label='Submit', primary=True),
                    ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
                ]
            )
        ]
    )
    return card

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]

async def render_program_description(q, box):
    '''
    Renders the program description in an article card
    :param q: instance of Q for wave query
    :param location: page location to display
    '''
    title = q.user.X_degree_program # program name


    query = '''
        SELECT description, info, learn, certification
        FROM program_descriptions WHERE program_id = ?
    '''
    row = await get_query_one(q, query, params=(q.user.X_program_id,))
    if row:
        #major = '\n##' + title + '\n\n'
        frontstuff = "\n\n#### What You'll Learn\nThrough your coursework, you will learn how to\n"
        if int(q.user.X_program_id) in (4, 24, 29):
            content = row['info'] + '\n\n' + row['description']
        else:
            content = row['description'] + frontstuff + row['learn'] #+ '\n\n' + row['certification']

        card = add_card(q, 'program_description', ui.markdown_card(
            box=box, 
            title=title,
            content=content
        ))
        #card = add_card(q, 'program_description', ui.article_card(
        #    box=box, 
        #    title=title,
        ##    content=row['description'] + row['']
        #    content=content
        #))
        return card

async def render_program_dashboard(q, box):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    flex=True: location is required
    flex=False: box is required
    '''
    title = q.user.X_degree_program # program name

    #if q.user.X_menu_degree == '2':

    # get program summary for bachelor's degrees
    query = 'SELECT * FROM program_requirements WHERE program_id = ?'
    row = await get_query_one(q, query, params=(q.user.X_program_id,))
    if row:
        card = add_card(q, 'major_dashboard', ui.form_card(
            box=box,
            items=[
                #ui.text(title + ': Credits', size=ui.TextSize.L),
                ui.text('Credits', size=ui.TextSize.L),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Major',
                            value=str(row['major']),
                            #caption='Credits',
                            icon='Trackers',
                            icon_color='#135f96'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Required',
                            value=str(row['related_ge'] + row['related_elective']),
                            #caption='Credits',
                            icon='News',
                            icon_color='#a30606'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='General Education',
                            value=str(row['remaining_ge']),
                            #caption='Remaining GE',
                            icon='TestBeaker',
                            #icon_color='#787800'
                            icon_color='#3c3c43'
                    )]
                ),
                ui.stats(
                    items=[
                        ui.stat(
                            label='Elective',
                            value=str(row['remaining_elective']),
                            #caption='Remaining Elective',
                            icon='Media',
                            icon_color='#fdbf38'
                    )]
                ),
                ui.separator(),
                ui.stats(
                    items=[
                        ui.stat(
                            label='TOTAL',
                            value=str(row['total']),
                            #caption='Remaining Elective',
                            icon='Education',
                            icon_color='#da1a32 '
                    )]
                ),
            ])
        )
        return card
        #else: '#3c3c43' 
        #    pass
        #    # send a warning

async def render_program_table(q, df, box=None, location=None, width=None, height=None, flex=False, check=True, ge=False, elective=False):
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
        no_rows = (df['type'].str.upper() == record_type).sum() == 0

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
        df, collapsed=True, check=False
    )
    if result != '':
        groups.append(result)
        
    result = await _render_program_group(
        'Required Related Courses/General Education',
        'REQUIRED,GENERAL',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)
    
    result = await _render_program_group(
        'Required Related Courses/Electives',
        'REQUIRED,ELECTIVE',
        df, collapsed=True, check=check
    )
    if result != '':
        groups.append(result)

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
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='prerequisites', label='Show Prerequisites'),
                ]
        ))
    ]

    if flex:
        box = ui.box(location, height=height, width=width)

    #title = q.user.X_degree_program + ': Explore Required Courses'
    title = 'Explore Required Courses'
    card = add_card(q, 'program_table', ui.form_card(
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
    ))
    return card

async def render_program_coursework_table(q, box='1 3 5 7', location='middle_vertical', width='100%', height='500px', flex=False):
    '''
    Create program coursework requirement table
    '''
    #############
    query = '''
        SELECT 
            id,
            course, 
            course_type as type,
            title,
            credits,
            pre,
            pre_credits,
            substitutions,
            description
        FROM program_requirements_view
        WHERE program_id = ?
    '''
    df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_program_id,))
    q.client.program_df = df

    await render_program_table(q, df, box=box, location=location, width=width, height=height, flex=flex)

async def render_program(q):
    await render_program_description(q, box='1 3 7 2')
    await render_program_dashboard(q, box='7 5 1 5')
    await render_program_coursework_table(q, box='1 5 6 5')


##############################################################
####################  PROGRAM PAGE (END)   ###################
##############################################################

##############################################################
####################  COURSES PAGE (START) ###################
##############################################################

def render_courses_header(q, box='1 2 7 1'):
    content=f'**Program Selected**: {q.user.X_degree_program}'
    add_card(q, 'courses_header', ui.form_card(
        box=box,
        items=[
            ui.text_l(content),
            #ui.text('We will guide you through this experience.')
        ]
    ))

async def get_catalog_program_sequence(q):
    query = 'SELECT * FROM catalog_program_sequence_view WHERE program_id = ?'
    #query = '''
    #    SELECT 
    #        a.seq, 
    #        a.course AS name,
    #        c.name as course_type,
    #        CASE
    #            WHEN INSTR(c.name, '_') > 0 
    #            THEN SUBSTR(c.name, 1, INSTR(c.name, '_') - 1)
    #            ELSE c.name
    #        END as type,
    #        b.credits,
    #        b.title,
    #        0 AS completed,
    #        0 AS term,
    #        0 AS session,
    #        0 AS locked,
    #        b.pre,
    #        b.pre_credits, 
    #        b.substitutions,
    #        b.description
    #    FROM 
    #        catalog_program_sequence a
    #    LEFT JOIN
    #        course_type c
    #    ON
    #        c.id = a.course_type_id
    #    LEFT JOIN
    #        classes b
    #    ON
    #        a.course = b.name
    #    WHERE 
    #        a.program_id = ?
    #'''
    try:
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_program_id,))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or return a specific value or message

    # Check if df is empty
    if df.empty:
        print("The query returned zero rows.")
        return None  # or return a specific value or message

    return df

async def get_student_progress_d3(q):
    query = '''
        SELECT * FROM student_progress_d3_view WHERE user_id = ?
    '''
    try:
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.X_user_id,))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or return a specific value or message

    # Check if df is empty
    if df.empty:
        print("The query returned zero rows.")
        return None  # or return a specific value or message

    return df

async def render_course_page_table(q, df, box=None, location=None, width=None, height=None, flex=False, check=True, ge=False, elective=False):
    '''
    Input comes from 
    q:
    df:
    location:
    cardname:
    width:
    height:
    '''
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
                ui.command(name='show_prereq', label='Show Prerequisites'),
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
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='show_prereq', label='Show Prerequisites'),
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

    if flex:
        box = ui.box(location, height=height, width=width)

    title = f'**{q.user.X_degree_program}**: Courses'
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
    return card

##############################################################
####################  COURSES PAGE (END)  ####################
##############################################################

##############################################################
####################  GE PAGE (START) ########################
##############################################################

# reset ge defaults if covered in  
async def get_ge_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['name'] + ': ' + row['title']) for row in rows]
    return choices

ge_query = "SELECT name, name || ': ' || title AS label FROM ge_view WHERE ge_id=? ORDER BY name"
ge_query_nopre = '''
    SELECT name, name || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
        AND pre='' 
        AND pre_credits=''
    ORDER BY name
'''
ge_credits_query = '''
    SELECT name, name || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? AND credits=? 
    ORDER BY name
'''
ge_pairs_query = '''
    SELECT 
        name, 
        name || ' & ' || substr(note, 27, 3) || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=9 AND credits=3
    ORDER BY name
'''

async def render_ge_comm_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    if flex:
        box = location
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
                value=q.user.X_ge_comm_p1 if (q.user.X_ge_comm_p1 is not None) else 'WRTG 111',
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (1,))
            ),
            ui.dropdown(
                name='ge_comm_2',
                label='2. WRTG 112 (3 credits)',
                value=q.user.X_ge_comm_p2 if (q.user.X_ge_comm_p2 is not None) else 'WRTG 112',
                disabled=False,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (2,))
            ),
            ui.dropdown(
                name='ge_comm_3',
                label='3. Another course (3 credits)',
                placeholder='(Select One)',
                value=q.user.X_ge_comm_p3 if (q.user.X_ge_comm_p3 is not None) else q.args.ge_comm_p3,
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (3,))
            ),
            ui.dropdown(
                name='ge_comm_4',
                label='4. Advanced writing course (3 credits)',
                placeholder='(Select One)',
                value=q.user.X_ge_comm_p4 if (q.user.X_ge_comm_p4 is not None) else q.args.ge_comm_p4,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (4,))
            ),
        ]
    )
    return card

async def render_ge_math_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Mathematics', size=ui.TextSize.L),
                ui.checkbox(name='ge_math_check', label='')
            ], justify='between', align='start'),
            ui.dropdown(
                name='ge_math',
                label='One Course (3 credits)',
                value=q.user.X_ge_math if (q.user.X_ge_math is not None) else q.args.ge_math,
                placeholder='(Select One)',
                trigger=True,
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (5,))
            ),
        ]
    )
    return card

async def render_ge_arts_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
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
                value=q.user.X_ge_arts_1 if (q.user.X_ge_arts_1 is not None) else q.args.ge_arts_1,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (6,))
            ),
            ui.dropdown(
                name='ge_arts_2',
                label='2. Course (3 credits)',
                value=q.user.X_ge_arts_2 if (q.user.X_ge_arts_2 is not None) else q.args.ge_arts_2,
                trigger=True,
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                # figure out how to omit choice selected in Course 1
                choices=await get_choices(q, ge_query, (6,))
            ),
        ]
    )
    return card

async def render_ge_science_card(q, menu_width, box='4 2 2 5', flex=False, location='grid'):
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
    card = ui.form_card(
        box=box,
        items=[
            ui.inline([
                ui.text('Biological and Physical Sciences', size=ui.TextSize.L),
                ui.checkbox(name='ge_science_check', label='')
            ], justify='between', align='start'),
            #ui.text('Select one of the following:', size=ui.TextSize.L),
            #ui.separator(label='1. Select one of the following three choices:'),
            ui.dropdown(
                name='ge_bio_1a',
                label='1. Lecture & Lab (4 credits): Select one',
                value=q.user.X_ge_bio_1a if (q.user.X_ge_bio_1a is not None) else q.args.ge_bio_1a,
                trigger=True,
                placeholder='(Combined Lecture & Lab)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query, (7,))
            ),
            ui.dropdown(
                name='ge_bio_1c',
                #label='Separate Lecture and Laboratory',
                value=q.user.X_ge_bio_1c if (q.user.X_ge_bio_1c is not None) else q.args.ge_bio_1c,
                trigger=True,
                placeholder='or (Separate Lecture & Lab)',
                width=menu_width,
                choices=await get_choices(q, ge_pairs_query, ())
            ),
            ui.dropdown(
                name='ge_bio_1b',
                #label='For Science Majors and Minors only:',
                value=q.user.X_ge_bio_1b if (q.user.X_ge_bio_1b is not None) else q.args.ge_bio_1b,
                trigger=True,
                placeholder='or (Science Majors and Minors)',
                #placeholder='or (Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (8,))
            ),
            #ui.separator(label='Select an additional science course:'),
            #nopre=True # check for easy classes by selecting those w/o prerequisites
            ui.dropdown(
                name='ge_bio_2',
                label='2. An additional course (3 credits)',
                value=q.user.X_ge_bio_2 if (q.user.X_ge_bio_2 is not None) else q.args.ge_bio_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query_nopre if nopre else ge_query, (10,))
                #choices=await get_choices(q, ge_query_nopre, (10,))
            ),
        ]
    )
    return card

async def render_ge_beh_card(q, menu_width, box='1 3 3 4', flex=False, location='grid'):
    if flex:
        box = location
    nopre = True # pick this value up from checkbox
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
                value=q.user.X_ge_beh_1 if (q.user.X_ge_beh_1 is not None) else q.args.ge_beh_1,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                #choices=await get_choices(q, ge_query, (11,))
                choices=await get_choices(q, ge_query_nopre if nopre else ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Course (3 credits)',
                value=q.user.X_ge_beh_2 if (q.user.X_ge_beh_2 is not None) else q.args.ge_beh_2,
                trigger=True,
                popup='always',
                placeholder='(Select One)',
                required=True,
                width=menu_width,
                choices=await get_choices(q, ge_query_nopre if nopre else ge_query, (11,))
                #choices=await get_choices(q, ge_query, (11,))
            ),
        ]
    )
    return card

async def render_ge_research_card(q, menu_width, box='1 3 3 4', flex=False, location='grid'):
    if flex:
        box = location
    # make some defaults based on area of program chosen:
    if q.user.X_area_of_study == 1:
        q.user.X_ge_res_1 = 'PACE 111B'
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
                value=q.user.X_ge_res_1 if (q.user.X_ge_res_1 is not None) else q.args.ge_res_1,
                # default value will depend on the major chosen
                trigger=True,
                placeholder='(Select One)',
                popup='always',
                width=menu_width,
                choices=await get_choices(q, ge_query, (12,))
            ),
            ui.dropdown(
                name='ge_res_2',
                label='2. Research Skills / Professional Development (1 credit)',
                value=q.user.X_ge_res_2 if (q.user.X_ge_res_2 is not None) else 'LIBS 150',
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (13,))
            ),
            ui.dropdown(
                name='ge_res_3',
                label='3. Computing or IT (3 credits)',
                value=q.user.X_ge_res_3 if (q.user.X_ge_res_3 is not None) else q.args.ge_res_3,
                trigger=True,
                required=True,
                placeholder='(Select 3-credit Course)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,3))
            ),
           ui.dropdown(
                name='ge_res_3a',
                label='[or three 1-credit courses]:',
                required=True,
                value=q.user.X_ge_res_3a if (q.user.X_ge_res_3a is not None) else q.args.ge_res_3a,
                trigger=True,
                placeholder='(Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3b',
                #label='Computing or Information Technology (1 credit)',
                value=q.user.X_ge_res_3b if (q.user.X_ge_res_3b is not None) else q.args.ge_res_3b,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
            ui.dropdown(
                name='ge_res_3c',
                #label='Computing or Information Technology (1 credit each)',
                value=q.user.X_ge_res_3c if (q.user.X_ge_res_3c is not None) else q.args.ge_res_3c,
                trigger=True,
                placeholder='and (Select 1-credit Course)',
                width=menu_width,
                choices=await get_choices(q, ge_credits_query, (14,1))
            ),
        ]
    )
    return card

##############################################################
####################  GE PAGE (END)   ########################
##############################################################

###############################################################
####################  SCHEDULE PAGE (START) ###################
###############################################################

def d3plot(html, box='1 2 5 6', flex=False, location='horizontal', height='500px', width='100%'):
    if flex:
        box=ui.box(location, height=height, width=width)
    card = ui.frame_card(
        box=box,
        #title='Course Schedule',
        title='',
        content=html
    )
    return card

async def render_schedule_page_table(q, box=None, location=None, width=None, height=None, flex=False):
    '''
    Input comes from 
    q:
    df:
    location:
    cardname:
    width:
    height:
    '''
    df = q.user.X_schedule_df

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
                ui.command(name='show_prereq', label='Show Prerequisites'),
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
                tags=UMGC_tags
            )
        ),
        ui.table_column(name='term', label='Term', max_width='50', data_type='number'),        
        ui.table_column(name='session', label='Session', max_width='80', data_type='number'),        
        ui.table_column(name='menu', label='Menu', max_width='150',
            cell_type=ui.menu_table_cell_type(name='commands', 
                commands=[
                    ui.command(name='view_description', label='Course Description'),
                    ui.command(name='show_prereq', label='Show Prerequisites'),
                    ui.command(name='change_time', label='Move Class'),
                    ui.command(name='lock_class', label='Lock Class'),
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
                str(row['term']),
                str(row['session']),
            ]
        ) for _, row in df.iterrows()
    ]

    if flex:
        box = ui.box(location, height=height, width=width)

    title = f'**{q.user.X_degree_program}**: Courses'
    #title = 'Courses'
    card = add_card(q, 'course_table', ui.form_card(
        box=box,
        items=[
            #ui.inline(justify='between', align='center', items=[
            #    ui.text(title, size=ui.TextSize.L),
            #    ui.button(name='schedule_coursework', label='Schedule', 
            #        #caption='Description', 
            #        primary=True, disabled=False)
            #]),
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
    return card

###############################################################
####################  SCHEDULE PAGE (END)  ####################
###############################################################

#############################################################
####################  PROJECT PAGE (START) ##################
#############################################################

async def render_project_table(data, box='1 1 5 5', flex=False, location='middle_vertical', title='Project Status Table', height='520px'):

    if flex:
        box=location

    _project_table_columns = [
        ui.table_column(
            name='id',
            label='Id',
            sortable=True,
            min_width='40px'
        ),
        ui.table_column(
            name='rank',
            label='Rank',
            sortable=True,
            min_width='60px'
        ),
        ui.table_column(
            name='category',
            label='Category',
            sortable=True,
            #filterable=True,
            #searchable=True,
            min_width='120px'
        ),
        ui.table_column(
            name='description',
            label='Description',
            cell_type=ui.markdown_table_cell_type(),
            min_width='300px',
            searchable=True
        ),
        ui.table_column(
            name='status',
            label='Status',
            cell_type=ui.progress_table_cell_type(),
            sortable=True,
            min_width='100px'
        ),
        ui.table_column(
            name='tags',
            label='Tags',
            cell_type=ui.tag_table_cell_type(
                name='',
                tags=[
                    ui.tag(label='Database', color='$green'),
                    ui.tag(label='UI', color='$blue'),
                    ui.tag(label='Wave', color='$orange'),
                    ui.tag(label='Code', color='$purple'),
                    ui.tag(label='Data', color='$red')
                ]
            ),
            searchable=True
        ),
        ui.table_column(
            name='menu',
            label='Menu',
            cell_type=ui.menu_table_cell_type(
                commands=[
                    ui.command(name='view_transaction', label='View Transaction', icon='Shop'),
                    ui.command(name='view_image', label='View Image', icon='ImageSearch')
                ]
            ),
            min_width='60px'
        )
    ]
    _project_table_rows = [
        ui.table_row(
            name=row['id'],
            cells=[
                row['id'],
                row['rank'],
                row['category'],
                row['description'],
                row['status'],
                row['tags']
            ]
        ) for row in data
    ]
    card = ui.form_card(
        box=box,
        items=[
            ui.text(title, size=ui.TextSize.XL),
            ui.table(
                name='transactions',
                columns=_project_table_columns,
                rows=_project_table_rows,
                # pagination=False,
                groupable=True,
                # resettable=True,
                # downloadable=True,
                events=['page_change'],
                height=height
            ),
        ]
    )
    return card

#############################################################
####################  PROJECT PAGE (END)   ##################
#############################################################

warning_example_card = ui.form_card(
    box='1 1 4 7',
    items=[
        ui.message_bar(type='blocked', text='This action is blocked.'),
        ui.message_bar(type='error', text='This is an error message'),
        ui.message_bar(type='warning', text='This is a warning message.'),
        ui.message_bar(type='info', text='This is an information message.'),
        ui.message_bar(type='success', text='This is an success message.'),
        ui.message_bar(type='danger', text='This is a danger message.'),
        ui.message_bar(type='success', text='This is a **MARKDOWN** _message_.'),
        ui.message_bar(type='success', text='This is an <b>HTML</b> <i>message</i>.'),
    ]
)

###########


