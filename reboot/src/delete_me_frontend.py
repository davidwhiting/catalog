from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List

meta_card = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
    ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
        ui.zone('sidebar', size='250px'),
        ui.zone('body', zones=[
            ui.zone('header'),
            ui.zone('content', zones=[
                # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                ui.zone('vertical'),
                ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
            ]),
        ]),
    ])
])])

def return_sidebar(q: Q):
    return ui.nav_card(
        box='sidebar', color='primary', title='My App', subtitle="Let's conquer the world!",
        value=f'#{q.args["#"]}' if q.args['#'] else '#page1',
        image='https://wave.h2o.ai/img/h2o-logo.svg', items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#page1', label='Home'),
                ui.nav_item(name='#page2', label='Charts'),
                ui.nav_item(name='#page3', label='Grid'),
                ui.nav_item(name='#page4', label='Form'),
            ]),
    ])

header_card = ui.header_card(
    box='header', title='', subtitle='',
    secondary_items=[ui.textbox(name='search', icon='Search', width='400px', placeholder='Search...')],
    items=[
        ui.persona(title='John Doe', subtitle='Developer', size='xs',
                   image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
    ]
)
