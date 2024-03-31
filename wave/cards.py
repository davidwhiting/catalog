from h2o_wave import ui
from typing import Optional, List

import sys

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

def meta_card():
    card = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('header'),
        ui.zone('content', zones=[
            # Specify various zones and use the one that is currently needed. Empty zones are ignored.
            ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
            ui.zone('top_vertical'),
            ui.zone('middle_horizontal', direction=ui.ZoneDirection.ROW),
            ui.zone('middle_vertical'),
            ui.zone('horizontal', direction=ui.ZoneDirection.ROW), # delete eventually
            ui.zone('vertical'),                                   # delete eventually
            ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'), # delete eventually
            ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
            ui.zone('bottom_vertical'),
        ]),
        ui.zone('footer'),
    ])])
    return card 

def header_card(q):
    card = ui.header_card(
        box='header', title='My app', subtitle="Let's conquer the world",
        image='https://wave.h2o.ai/img/h2o-logo.svg',
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                ui.tab(name='#major', label='Major'),
                ui.tab(name='#page3', label='Grid'),
            ]),
        ],
        items=[
            ui.persona(title='John Doe', subtitle='Developer', size='xs',
                       image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
        ]
    )
    return card

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

    #states = [
    #    ('q.app', q.app),
    #    ('q.user', q.user),
    #    ('q.client', q.client),
    #    ('q.events', q.events),
    #    ('q.args', q.args)
    #]

def render_debug_card(q, location='bottom_horizontal', width='33%'):
    content = f'''
### q.args.degree value:
{q.args.degree}

### q.args.area_of_study value:
{q.args.area_of_study}

### q.args.program value:
{q.args.program}

### q.args value:
{q.args}

    '''
    return ui.markdown_card(
        box=ui.box(location, width=width), 
        title='Debugging Information', 
        content=content 
    )

def render_debug_client_card(q, location='bottom_horizontal', width='33%'):
    content = f'''
### q.client.degree value:
{q.client.degree}

### q.client.area_of_study value:
{q.client.area_of_study}

### q.client.program value:
{q.client.program}

### q.client value:
{q.client}

    '''
    return ui.markdown_card(
        ui.box(location, width=width), 
        title='Client Debugging Information', 
        content=content 
    )
def render_debug_user_card(q, location='bottom_horizontal', width='33%'):
    content = f'''
### q.app values:
{q.app}

### q.user values:
{q.user}

    '''
    return ui.markdown_card(
        ui.box(location, width=width), 
        title='User Debugging Information', 
        content=content 
    )

def render_debug(q, location='bottom_horizontal', width='25%'):
    add_card(q, 'debug_info', render_debug_card(q, location=location, width=width)) 
    add_card(q, 'debug_client_info', render_debug_client_card(q,  location=location, width=width)) 
    add_card(q, 'debug_user_info', render_debug_user_card(q,  location=location, width=width)) 

async def get_query_one(q, query, params=()):
    c = q.user.c 
    c.execute(query, params)
    row = c.fetchone()
    return row

async def get_query(q, query, params=()):
    c = q.user.c 
    c.execute(query, params)
    rows = c.fetchall()
    return rows

async def get_choices(q, query, params=()):
    rows = await get_query(q, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
    return choices

async def render_home_cards(q, location='top_horizontal', width='25%'):
    add_card(q, 'student_guest', ui.wide_info_card(
        box=ui.box(location, width=width),
        name='',
        icon='Contact',
        title='Guests',
        caption='Login not required to use this app.'
    ))
    add_card(q, 'login',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='login',
            title='Login',
            caption='User roles: *admin*, *coach*, *student*, *prospect*.',
            icon='Signin')
    )
    add_card(q, 'import',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='import',
            title='Import',
            caption='Future state: Import UMGC student info.',
            icon='Import')
    )
    add_card(q, 'personalize',
        ui.wide_info_card(
            box=ui.box(location, width=width),
            name='person',
            title='Personalize',
            caption='User adds new info or confirms imported info.',
            icon='UserFollowed')
    )

def render_major_recommendation_card(q, location='top_horizontal', width='350px'):
    card = ui.form_card(
        box=ui.box(location, width=width),
        items=[
            ui.choice_group(
                name='recommendation_group',
                label='Recommend a major based on ...',
                choices=[
                    ui.choice('A', label='My interests'),
                    ui.choice('B', label='My skills'),
                    ui.choice('C', label='Students like me'),
                    ui.choice('D', label='The shortest time to graduate'),
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

# doesn't work yet
# ValueError: card must be dict or implement .dump() -> dict

async def render_dropdown_menus(q, location='top_horizontal', menu_width='280px'):
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
    card = ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='degree',
                label='Degree',
                value=q.client.degree if (q.client.degree is not None) else q.args.degree,
                trigger=True,
                width=menu_width,
                choices=await get_choices(q, degree_query)
            ),
            ui.dropdown(
                name='area_of_study',
                label='Area of Study',
                value=q.client.area_of_study if (q.client.area_of_study is not None) else \
                    q.args.area_of_study,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=None if (q.client.degree is None) else \
                    await get_choices(q, area_query, (q.client.degree,))
            ),
            ui.dropdown(
                name='program',
                label='Program',
                value=q.client.program if (q.client.program is not None) else q.args.program,
                trigger=True,
                disabled=False,
                width=menu_width,
                choices=None if (q.client.area_of_study is None) else \
                    await get_choices(q, program_query, (q.client.degree, q.client.area_of_study))
            )
        ]
    )
    return card

async def get_program_title(q, program_id):
    query = '''
        SELECT b.name || ' in ' || a.name as title
        FROM programs a, degrees b 
        WHERE a.id = ? AND a.degree_id = b.id 
    '''
    row = get_query_one(q, query, params=(program_id,))
    return row['title']
