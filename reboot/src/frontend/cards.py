## This file should contain cards but generally not place them.
## Thus, cards are either defined by a function (because they have to access Q)
## or they are an object themselves.

from h2o_wave import Q, ui, main, app, run_on, on, data, copy_expando, expando_to_dict
from typing import Optional, List
import traceback
import sys

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
                ui.nav_item(name='#courses', label='Courses'),
                ui.nav_item(name='#schedule', label='Schedule'),
            ]),
        ]
    )

header_card = ui.header_card(
    box='header', 
    title='UMGC Registration Assistant', 
    subtitle='',
    #subtitle="Registration Assistant",
    #title='', subtitle='',
    #secondary_items=[
    #    ui.textbox(name='search', icon='Search', width='400px', placeholder='Search...')],
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
            #ui.zone('top_vertical'),
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
