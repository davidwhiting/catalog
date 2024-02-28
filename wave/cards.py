import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

def select_semester(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='first', 
                label='Start Term', 
                value=q.args.start_term,
                trigger=True,
                width=menu_width,
                choices=[
                    ui.choice(label="Spring 2024"),
                    ui.choice(label="Summer 2024"),
                    ui.choice(label="Fall 2024"),
                    ui.choice(label="Winter 2025"),
                ]
            ),
        ]
    )

def dropdown_menus(q):
    menu_width = '250px'
    return ui.form_card(
        box='horizontal',
        items=[
            ui.inline(
                items=[
                    ui.dropdown(
                        name='degree', 
                        label='Degree', 
                        value=q.args.degree,
                        trigger=True,
                        width=menu_width,
                        choices=[
                            ui.choice(name='AS', label="Associate"),
                            ui.choice(name='BS', label="Bachelor's"),
                            ui.choice(name='MS', label="Master's"),
                            ui.choice(name='DC', label="Doctorate"),
                            ui.choice(name='UC', label="Undergraduate Certificate"),
                            ui.choice(name='GC', label="Graduate Certificate")
                    ]),
                    ui.dropdown(
                        name='area_of_study', 
                        label='Area of Study', 
                        value=q.args.area_of_study,
                        trigger=False,
                        disabled=False,
                        width=menu_width,
                        choices=[
                            ui.choice(name='BM', label='Business & Management'),
                            ui.choice(name='CS', label='Cybersecurity'),
                            ui.choice(name='DA', label='Data Analytics'),
                            ui.choice(name='ET', label='Education & Teaching'),
                            ui.choice(name='HS', label='Healthcare & Science'),
                            ui.choice(name='LA', label='Liberal Arts & Communications'),
                            ui.choice(name='PS', label='Public Safety'),
                            ui.choice(name='IT', label='IT & Computer Science')
                    ]),
                    ui.dropdown(
                        name='major', 
                        label='Major', 
                        value=q.args.major,
                        trigger=False,
                        disabled=False,
                        width=menu_width,
                        choices=[
                            ui.choice(name='AC', label='Accounting'),
                            ui.choice(name='BA', label='Business Administration'),
                            ui.choice(name='FI', label='Finance'),
                            ui.choice(name='HR', label='Human Resource Management'),
                            ui.choice(name='MS', label='Management Studies'),
                            ui.choice(name='MK', label='Marketing'),
                    ]),
                ]
            )
        ]
    )

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
meta = ui.meta_card(
    box='',
    title='UMGC Wave App',
    theme='ember',
    layouts=[
        ui.layout(
            breakpoint='xs',
            min_height='100vh',
#           max_width='1200px',
            max_width='100vw',
            zones=[
                ui.zone('header'),
                ui.zone('content', size='1', zones=[
                    ui.zone('horizontal', direction=ui.ZoneDirection.COLUMN, justify='center'),
                    ui.zone('horizontal2', direction=ui.ZoneDirection.ROW, size='1', 
                        zones=[
                           ui.zone('left1',  size='25%', direction=ui.ZoneDirection.COLUMN),
                           ui.zone('left2',  size='25%', direction=ui.ZoneDirection.COLUMN),
                           ui.zone('right1', size='49%', direction=ui.ZoneDirection.COLUMN),
                           ui.zone('right2', size= '1%', direction=ui.ZoneDirection.COLUMN),
                    ]),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center', 
                        zones=[
                        #   ui.zone('leftgrid', size='5%'),
                           ui.zone('midgrid', size='80%'),
                           ui.zone('rightgrid', size='20%', direction=ui.ZoneDirection.COLUMN),
                    ]),
                    ui.zone('slider', direction=ui.ZoneDirection.ROW, justify='center'),
                    ui.zone('notes', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center', 
                        zones=[
                           ui.zone('leftnote',  size='70%'),
                           ui.zone('rightnote', size='30%'),
                    ]),
                    
                ]),
                ui.zone(name='footer'),
            ]
        )
    ]
)

meta_new = ui.meta_card(
        box='', 
        title='UMGC Wave App',
        theme='ember',
        layouts=[
            ui.layout(
                breakpoint='xs', 
                min_height='100vh', 
                zones=[
                    ui.zone('header'),
                    ui.zone('content', zones=[
                        # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('dashboard', direction=ui.ZoneDirection.ROW),
                        ui.zone('d3', direction=ui.ZoneDirection.ROW),
#                        ui.zone('display', zones=[
#                            ui.zone('display_left', width='80%'),
#                            ui.zone('display_right', width='20%')
#                        ]),
                        ui.zone('vertical'),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )

toggle = ui.form_card(box='rightgrid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

transfer_toggle = ui.form_card(box='grid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

footer = ui.footer_card(
    box='footer',
    caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
    '''
)

markdown = ui.form_card(
    box='leftnote',
    items=[ui.text(templates.sample_markdown)]
)

#image_path, = await q.site.upload(['umgc-logo.png'])

def header(image_path, q):
    result = ui.header_card(    
        box='header',
        title='UMGC Programs',
        subtitle="Registration Assistant",
        image=image_path,
        secondary_items=[
            ui.tabs(name='tabs', 
#                    value=f'#{q.args["#"]}' if q.args['#'] else '#page0', 
                    value='#page1', 
#                    link=True, 
                    items=[
                ui.tab(name='#page0', label='Home'),
                ui.tab(name='#page1', label='Select Major'),
                ui.tab(name='#page2', label='Schedule Courses'),
                ui.tab(name='#page3', label='Electives'),
                ui.tab(name='#page4', label='Student Info'),
            ]),
        ],
        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)]
    )
    return result

def header_new_old(image_path, q):
    result = ui.header_card(
        box='header', 
        title='UMGC Programs',
        subtitle="Registration Assistant",
        image=image_path,
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                ui.tab(name='#major', label='Select Major'),
                ui.tab(name='#courses', label='Schedule Courses'),
                ui.tab(name='#electives', label='Electives'),
#                ui.tab(name='#student', label='Student Info'),
            ]),
        ],
#        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
        items=[
            ui.persona(title='John Doe', subtitle='Student', size='xs',
                       image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
        ]
    )
    return result

def header_new(image_path, q):
    image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'

    result = ui.header_card(
        box='header', 
        title='UMGC Programs',
        subtitle="Registration Assistant",
        image=image_path,
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                ui.tab(name='#major', label='Select Major'),
                ui.tab(name='#courses', label='Schedule Courses'),
                ui.tab(name='#electives', label='Electives'),
#                ui.tab(name='#student', label='Student Info'),
            ]),
        ],
#        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
        items=[
            ui.persona(title='John Doe', subtitle='Student', size='xs', image=image),
        ]
    )
    return result

#person_image = 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'
#header_menu_commands = [
#    ui.command(name='profile', label='Profile', icon='Contact'),
#    ui.command(name='preferences', label='Preferences', icon='Settings'),
#    ui.command(name='logout', label='Logout', icon='SignOut'),
#]

#async def serve(q: Q):
#    if not q.client.initialized:
#        q.page['example'] = ui.form_card(box='1 1 2 3', items=[])
#        q.client.initialized = True
#    if 'profile' in q.args and not q.args.show_form:
#        q.page['example'].items = [
#            ui.text(f'profile={q.args.profile}'),
#            ui.text(f'preferences={q.args.preferences}'),
#            ui.text(f'logout={q.args.logout}'),
#            ui.button(name='show_form', label='Back', primary=True),
#        ]
#    else:
#        q.page['example'].items = [
#            ui.menu(image=image, items=commands),
#            ui.menu(icon='Add', items=commands),
#            ui.menu(label='App', items=commands),
#            ui.menu(items=commands)
#        ]
#    await q.page.save()

def d3plot(html):
    result = ui.frame_card(
        box=ui.box('midgrid', height='600px', width='1000px'),
        title='Tentative Course Schedule',
        content=html
    )
    return result

def d3plot_new(html, location='horizontal'):
    result = ui.frame_card(
        box=ui.box(location, height='500px', width='100%'),
        title='Tentative Course Schedule',
        content=html
    )
    return result

def step3(q):
        # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='student_reset', label='Finish', primary=True),
        ])
    ]


def stats(D):
    return ui.form_card(
        box='horizontal', items=[
            ui.stats(justify='between', items=[
                ui.stat(label='Credits', 
                        value=str(D['total_credits_remaining']), 
                        caption='Credits Remaining', 
                        icon='LearningTools'),            
                ui.stat(label='Tuition', 
                        value=D['next_term_cost'], 
                        caption='Estimated Tuition', 
                        icon='Money'),
                ui.stat(label='Terms Remaining', 
                        value=str(D['terms_remaining']), 
                        caption='Terms Remaining', 
                        icon='Education'),
                ui.stat(label='Finish Date', 
                        value=D['completion_date'], 
                        caption='(Estimated)', 
                        icon='SpecialEvent'),
                ui.stat(label='Total Tuition', 
                        value=D['total_cost_remaining'], 
                        caption='Estimated Tuition', 
                        icon='Money'),
            ])
        ]
    )

#    q.page['tall_stats'] = ui.tall_stats_card(
##        box=ui.box('right2', height='200px',),
#        box=ui.box('left2'),
#        items=[
#            ui.stat(label='FINISH DATE', value=completion_date),
#            ui.stat(label='TERMS REMAINING', value=str(terms_remaining)),
#            ui.stat(label='CREDITS LEFT', value=str(total_credits_remaining)), 
#        ]
#    )

def chart1(box='horizontal'): 
    return ui.plot_card(
        box=box,
        title='Chart 1',
        data=data('category country product price', 10, rows=[
            ('G1', 'USA', 'P1', 124),
            ('G1', 'China', 'P2', 580),
            ('G1', 'USA', 'P3', 528),
            ('G1', 'China', 'P1', 361),
            ('G1', 'USA', 'P2', 228),
            ('G2', 'China', 'P3', 418),
            ('G2', 'USA', 'P1', 824),
            ('G2', 'China', 'P2', 539),
            ('G2', 'USA', 'P3', 712),
            ('G2', 'USA', 'P1', 213),
        ]),
        plot=ui.plot([ui.mark(type='interval', x='=product', y='=price', color='=country', stack='auto',
                              dodge='=category', y_min=0)])
)

def test_table(location='vertical'):
    return ui.form_card(box=location, items=[
        ui.table(
            name='table',
            downloadable=True,
            resettable=True,
            groupable=True,
            columns=[
                ui.table_column(name='text', label='Process', searchable=True),
                ui.table_column(
                    name='tag', 
                    label='Status', 
                    filterable=True, 
                    cell_type=ui.tag_table_cell_type(
                        name='tags',
                        tags=[
                            ui.tag(label='FAIL', color='$red'),
                            ui.tag(label='DONE', color='#D2E3F8', label_color='#053975'),
                            ui.tag(label='SUCCESS', color='$mint'),
                        ]
                    )
                )
            ],
            rows=[
                ui.table_row(name='row1', cells=['Process 1', 'FAIL']),
                ui.table_row(name='row2', cells=['Process 2', 'SUCCESS,DONE']),
                ui.table_row(name='row3', cells=['Process 3', 'DONE']),
                ui.table_row(name='row4', cells=['Process 4', 'FAIL']),
                ui.table_row(name='row5', cells=['Process 5', 'SUCCESS,DONE']),
                ui.table_row(name='row6', cells=['Process 6', 'DONE']),
            ]
        )
    ])
