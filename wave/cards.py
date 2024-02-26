import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates

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

toggle = ui.form_card(box='rightgrid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

footer = ui.footer_card(
    box='footer',
    caption='Made using [H2O Wave](https://wave.h2o.ai).'
)

markdown = ui.form_card(
    box='leftnote',
    items=[ui.text(templates.sample_markdown)]
)

#image_path, = await q.site.upload(['umgc-logo.png'])

def header(image_path, q=Q):
    result = ui.header_card(    
        box='header',
        title='UMGC Curriculum Assistant',
        subtitle="Title TBD",
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

def d3plot(html):
    result = ui.frame_card(
        box=ui.box('midgrid', height='600px', width='1000px'),
        title='Tentative Course Schedule',
        content=html
    )
    return result

def stats(D):
    result = ui.form_card(
        box='horizontal', items=[
            ui.stats(justify='between', items=[
                ui.stat(label='Credits', 
                        value=str(D['total_credits_remaining']), 
                        caption='Credits Remaining', 
                        icon='Education'),            
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

#menu_width = '250px'
#
#dropdown_menus = ui.form_card(
#    box='horizontal',
#    items=[
#        ui.inline(
#            items=[
#                ui.dropdown(
#                    name='degree', 
#                    label='Degree', 
#                    value=q.args.degree,
#                    trigger=True,
#                    width=menu_width,
#                    choices=[
#                        ui.choice(name='AS', label="Associate"),
#                        ui.choice(name='BS', label="Bachelor's"),
#                        ui.choice(name='MS', label="Master's"),
#                        ui.choice(name='DC', label="Doctorate"),
#                        ui.choice(name='UC', label="Undergraduate Certificate"),
#                        ui.choice(name='GC', label="Graduate Certificate")
#                ]),
#                ui.dropdown(
#                    name='area_of_study', 
#                    label='Area of Study', 
#                    value=q.args.area_of_study,
#                    trigger=False,
#                    disabled=False,
#                    width=menu_width,
#                    choices=[
#                        ui.choice(name='BM', label='Business & Management'),
#                        ui.choice(name='CS', label='Cybersecurity'),
#                        ui.choice(name='DA', label='Data Analytics'),
#                        ui.choice(name='ET', label='Education & Teaching'),
#                        ui.choice(name='HS', label='Healthcare & Science'),
#                        ui.choice(name='LA', label='Liberal Arts & Communications'),
#                        ui.choice(name='PS', label='Public Safety'),
#                        ui.choice(name='IT', label='IT & Computer Science')
#                ]),
#                ui.dropdown(
#                    name='major', 
#                    label='Major', 
#                    value=q.args.major,
#                    trigger=False,
#                    disabled=False,
#                    width=menu_width,
#                    choices=[
#                        ui.choice(name='AC', label='Accounting'),
#                        ui.choice(name='BA', label='Business Administration'),
#                        ui.choice(name='FI', label='Finance'),
#                        ui.choice(name='HR', label='Human Resource Management'),
#                        ui.choice(name='MS', label='Management Studies'),
#                        ui.choice(name='MK', label='Marketing'),
#                ]),
#            ]
#        )
#    ]
#)
#