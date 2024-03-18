import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates
import utils

from utils import add_card

def render_debug_card(q, location='d3'):
    content = f'''
### All parameters?
{q}

### App Parameters
{q.app}

### User Parameters
{q.user}

### Client Parameters
{q.client}
    '''
    return ui.markdown_card(box=location, title='Debugging Information', content=content )

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

major_recommendation_card = ui.form_card(
    box=ui.box('top_horizontal', width='350px'),
    # box=ui.box('d3', width='300px'), # min width 200px
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
        #                ui.slider(name='slider', label='Max Credits per Term', min=1, max=15, step=1, value=9),
        ui.inline(
            items=[
                ui.button(name='show_recommendations', label='Submit', primary=True),
                ui.button(name='clear_recommendations', label='Clear', primary=False),  # enable this
            ]
        )
    ]
)

def render_tag_column(width='120'):
    result = ui.table_column(
        name='tag', 
        label='Type', 
        max_width=width,
        filterable=True,
        cell_type=ui.tag_table_cell_type(
            name='tags',
            tags=[
                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                ui.tag(label='REQUIRED', color='$red'),
                ui.tag(label='GENERAL', color='#046A38'),
                ui.tag(label='MAJOR', color='#1565C0'),
            ]
        )
    )
    return result

tag_column = ui.table_column(
    name='tag', 
    label='Type', 
    min_width='100',
    filterable=True,
    cell_type=ui.tag_table_cell_type(
        name='tags',
        tags=[
            ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
            ui.tag(label='REQUIRED', color='$red'),
            ui.tag(label='GENERAL', color='#046A38'),
            ui.tag(label='MAJOR', color='#1565C0'),
        ]
    )
)

def create_table_group(group_name, record_type, records, collapsed):
    return ui.table_group(group_name, [
        ui.table_row(
            name=str(record['seq']),
            cells=[
                record['name'], 
                record['title'], 
                str(record['credits']), 
                #record['description'],
                record['type'].upper(), 
            ]
        ) for record in records if record['type'].upper() == record_type
    ], collapsed=collapsed)


def render_course_table2(q, records,
                         which=['MAJOR','REQUIRED'],
                         title='',
                         location='middle_horizontal',
                         table_height='100%',
                         table_width='100%'):
    # Renders a table for the courses tab

    #table_name = 'table_' + '_'.join(which)
    table_name = 'table_render_course2'
    result = add_card(q, table_name, ui.form_card(
#        box=ui.box(location, width=table_width, height=table_height),
        box=ui.box(location),
        items=[
            #ui.text(title, size=ui.TextSize.L),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                #height='800px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='course', label='Course', searchable=True, min_width='100'),
                    ui.table_column(name='title', label='Title', searchable=True, min_width='180', max_width='300', cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', min_width='50', align ='center'),
                    #ui.table_column(name='description', label='Description', searchable=False, max_width='150',
                    #    cell_overflow='tooltip',
                    #    #cell_overflow='wrap',
                    #    #cell_type=ui.markdown_table_cell_type(target='_blank'),
                    #),
                    tag_column,
                    ui.table_column(name='menu', label='Menu', max_width='150',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                            #ui.command(name='delete', label='Delete'),
                        ])
                    )
                ],
                groups=[
                    create_table_group('Required Major Core Courses', 'MAJOR', records, False),
                    create_table_group('Required Related Courses', 'REQUIRED', records, True),
                    create_table_group('Selected General Education Courses', 'GENERAL', records, True),
                    create_table_group('Selected Elective Courses', 'ELECTIVE', records, True),
                ]
            )
        ]
    ))

    return result

def render_course_table(q, records, which=['MAJOR'], title='Major Required Courses', location='middle_horizontal', table_height='480px', table_width='700px'):
    # Renders a table for the courses tab

    table_name = 'table_' + '_'.join(which)

    result = add_card(q, table_name, ui.form_card(
        box=ui.box(location, width=table_width, height=table_height),
        items=[
            ui.text(title, size=ui.TextSize.XL),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='400px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='text', label='Course', searchable=False, max_width='100'),
                    ui.table_column(name='title', label='Title', searchable=False, max_width='180', cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', max_width='50'),
                    ui.table_column(
                        name='tag', 
                        label='Course Type', 
                        max_width='150',
                        filterable=True, 
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='description', label='Description', searchable=False, max_width='60',
                        cell_overflow='tooltip', 
                        #cell_overflow='wrap', 
                        #cell_type=ui.markdown_table_cell_type(target='_blank'),
                    ),

#                    ui.table_column(name='actions', label='Menu', max_width='150',
#                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
#                            ui.command(name='description', label='Course Description'),
#                            ui.command(name='prerequisites', label='Show Prerequisites'),
#                            #ui.command(name='delete', label='Delete'),
#                        ])
#                    )
                ],
                rows=[ui.table_row(
                    name=str(record['seq']),
                    cells=[
                        #str(record['seq']), 
                        record['name'], 
                        record['title'], 
                        str(record['credits']), 
                        record['type'].upper(), 
                        record['description'], 
                    ]
                ) for record in records if record['type'].upper() in which ]
            )
        ]
    ))

    return result


def render_ge_table(q, records, which=['GENERAL'], title='Select General Education Courses', location='middle_horizontal', table_height='500px', table_width='700px'):
    # Renders a table for the courses tab

    table_name = 'table_' + '_'.join(which)

    result = add_card(q, table_name, ui.form_card(
        box=ui.box(location, width=table_width, height=table_height),
        items=[
            ui.text(title, size=ui.TextSize.XL),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='400px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='text', label='Course', searchable=False),
                    ui.table_column(name='credits', label='Credits', data_type='number'),
                    ui.table_column(
                        name='tag', 
                        label='Course Type', 
                        filterable=True, 
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='actions', label='Menu',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                            #ui.command(name='delete', label='Delete'),
                        ])
                    )
                ],
                rows=[ui.table_row(
                    name=str(record['seq']),
                    cells=[
                        #str(record['seq']), 
                        record['name'], 
                        str(record['credits']), 
                        record['type'].upper(), 
                    ]
                ) for record in records if record['type'].upper() in which ]
            )
        ]
    ))

    return result

def render_elective_table(q, records, which=['ELECTIVE'], title='Select Elective Courses', location='middle_horizontal', table_height='500px', table_width='700px'):
    # Renders a table for the courses tab

    table_name = 'table_' + '_'.join(which)

    result = add_card(q, table_name, ui.form_card(
        box=ui.box(location, width=table_width, height=table_height),
        items=[
            ui.text(title, size=ui.TextSize.XL),        
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='400px',
                columns=[
                    #ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='text', label='Course', searchable=False),
                    ui.table_column(name='credits', label='Credits', data_type='number'),
                    ui.table_column(
                        name='tag', 
                        label='Course Type', 
                        filterable=True, 
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='actions', label='Menu',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                            #ui.command(name='delete', label='Delete'),
                        ])
                    )
                ],
                rows=[ui.table_row(
                    name=str(record['seq']),
                    cells=[
                        #str(record['seq']), 
                        record['name'], 
                        str(record['credits']), 
                        record['type'].upper(), 
                    ]
                ) for record in records if record['type'].upper() in which ]
            )
        ]
    ))

    return result

def select_semester(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='start_term', 
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

def dropdown_menus(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
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

def dropdown_menus_vertical(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
#            ui.inline(
#                items=[
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
#                ]
            #)
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
                zones=[
                    ui.zone('header'),
                    ui.zone('content', zones=[
                        # Specify various zones and use the one that is currently needed. 
                        # Empty zones are ignored.
                        ui.zone('top', zones=[
                            ui.zone('top_vertical'),
                            ui.zone('top_horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('dashboard', direction=ui.ZoneDirection.ROW),
                        ]),
                        ui.zone('middle', zones=[
                            ui.zone('middle_vertical'),
                            ui.zone('middle_horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('middle_horizontal2', direction=ui.ZoneDirection.ROW, wrap='stretch'),
                            ui.zone('d3', direction=ui.ZoneDirection.ROW),
#                           ui.zone('display', zones=[
#                               ui.zone('display_left', width='80%'),
#                               ui.zone('display_right', width='20%')
#                           ]),
                            #ui.zone('dashboard2', direction=ui.ZoneDirection.ROW),
                        ]),
                        ui.zone('bottom', zones=[
                            ui.zone('bottom_vertical'),
                            ui.zone('bottom_horizontal', direction=ui.ZoneDirection.ROW),
                            ui.zone('vertical'),
                            ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                        ]),
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

#def header_new_old(image_path, q):
#    result = ui.header_card(
#        box='header', 
#        title='UMGC Programs',
#        subtitle="Registration Assistant",
#        image=image_path,
#        secondary_items=[
#            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
#                ui.tab(name='#home', label='Home'),
#                ui.tab(name='#student', label='Student Info'),
#                ui.tab(name='#major', label='Major'),
#                ui.tab(name='#electives', label='Courses'),
#                ui.tab(name='#courses', label='Schedule'),
#            ]),
#        ],
##        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
#        items=[
#            ui.persona(title='John Doe', subtitle='Student', size='xs',
#                       image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'),
#        ]
#    )
#    return result

def get_header(image_path, q):
    persona_image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'
    commands = [
        ui.command(name='profile', label='Profile', icon='Contact'),
        ui.command(name='preferences', label='Preferences', icon='Settings'),
        ui.command(name='logout', label='Logout', icon='SignOut'),
    ]

    result = ui.header_card(
        box='header', 
        title='UMGC Programs',
        subtitle="Registration Assistant",
        image=image_path,
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                ui.tab(name='#student', label='Student Info'),
                ui.tab(name='#major', label='Select Major'),
                ui.tab(name='#courses', label='Select Courses'),
                ui.tab(name='#schedule', label='Set Schedule'),
            ]),
        ],
        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
#        items=[ui.persona(title='John Doe', subtitle='Student', size='xs', image=persona_image)]
    )
    return result



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

def d3plot(html, location='horizontal'):
    result = ui.frame_card(
        box=ui.box(location, height='500px', width='100%'),
        title='Tentative Course Schedule',
        content=html
    )
    return result


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

