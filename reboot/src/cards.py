from h2o_wave import Q, ui, data

def sidebar_card(q: Q):
    '''
    From sidebar
    '''
    return ui.nav_card(
        box='sidebar', color='primary', title='My App', subtitle="Let's conquer the world!",
        value=f'#{q.args["#"]}' if q.args['#'] else '#page1',
        image='https://wave.h2o.ai/img/h2o-logo.svg', items=[
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
    box='header', title='', subtitle='',
    secondary_items=[ui.textbox(name='search', icon='Search', width='400px', placeholder='Search...')],
    items=[
        ui.persona(title='John Doe', subtitle='Developer', size='xs',
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

meta_card_old = ui.meta_card(box='', 
    layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='200px'),
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

def return_meta_card() -> ui.meta_card:
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
            ])
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

page1_card1 = ui.tall_info_card(
    box='horizontal', name='', title='Speed',
    caption='The models are performant thanks to...', icon='SpeedHigh')
 
page1_card4 = ui.tall_article_preview_card(
    box=ui.box('vertical', height='600px'), title='How does magic work',
    image='https://images.pexels.com/photos/624015/pexels-photo-624015.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    content='''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Donec in erat augue. 
        '''
    )

page2_card1 = ui.plot_card(
    box='horizontal',
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
    plot=ui.plot([ui.mark(type='interval', x='=product', y='=price', color='=country', 
                          stack='auto', dodge='=category', y_min=0)])
)

page2_card2 = ui.plot_card(
    box='horizontal',
    title='Chart 2',
    data=data('date price', 10, rows=[
        ('2020-03-20', 124),
        ('2020-05-18', 580),
        ('2020-08-24', 528),
        ('2020-02-12', 361),
        ('2020-03-11', 228),
        ('2020-09-26', 418),
        ('2020-11-12', 824),
        ('2020-12-21', 539),
        ('2020-03-18', 712),
        ('2020-07-11', 213),
    ]),
    plot=ui.plot([ui.mark(type='line', x_scale='time', x='=date', y='=price', y_min=0)])
)

page2_card3 = ui.form_card(box='vertical', items=[ui.table(
        name='table',
        downloadable=True,
        resettable=True,
        groupable=True,
        columns=[
            ui.table_column(name='text', label='Process', searchable=True),
            ui.table_column(name='tag', label='Status', filterable=True, cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=[
                    ui.tag(label='FAIL', color='$red'),
                    ui.tag(label='DONE', color='#D2E3F8', label_color='#053975'),
                    ui.tag(label='SUCCESS', color='$mint'),
                ]
            ))
        ],
        rows=[
            ui.table_row(name='row1', cells=['Process 1', 'FAIL']),
            ui.table_row(name='row2', cells=['Process 2', 'SUCCESS,DONE']),
            ui.table_row(name='row3', cells=['Process 3', 'DONE']),
            ui.table_row(name='row4', cells=['Process 4', 'FAIL']),
            ui.table_row(name='row5', cells=['Process 5', 'SUCCESS,DONE']),
            ui.table_row(name='row6', cells=['Process 6', 'DONE']),
        ])
    ])

page3_card1 = ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
    caption='Lorem ipsum dolor sit amet')

page4_card1 = ui.form_card(box='vertical', items=[
    ui.stepper(name='stepper', items=[
        ui.step(label='Step 1'),
        ui.step(label='Step 2'),
        ui.step(label='Step 3'),
    ]),
    ui.textbox(name='textbox1', label='Textbox 1'),
    ui.buttons(justify='end', items=[
        ui.button(name='page4_step2', label='Next', primary=True),
    ]),
])

