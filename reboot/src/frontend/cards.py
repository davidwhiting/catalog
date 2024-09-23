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
                ui.nav_item(name='#page2', label='Page 2'),
                ui.nav_item(name='#page3', label='Page 3'),
                ui.nav_item(name='#page4', label='Page 4'),
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
