## This file should contain cards but generally not place them.
## Thus, cards are either defined by a function (because they have to access Q)
## or they are an object themselves.

from h2o_wave import Q, ui, main, app, run_on, on, data, copy_expando, expando_to_dict
from typing import Optional, List
import traceback
import sys

########################################################
####################  LAYOUT CARDS  ####################
########################################################

def sidebar_card(q: Q, home: str = '#page1') -> ui.NavCard:
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
                ui.nav_item(name='#page1', label='Page 1'),
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
