from h2o_wave import Q, ui, data
from typing import Optional, List
from utils import add_card

async def page1_1(q):

    for i in range(3):
        add_card(q, f'info{i}', ui.tall_info_card(box='horizontal', name='', title='Speed',
                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))

    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='600px'), title='How does magic work',
        image='https://images.pexels.com/photos/624015/pexels-photo-624015.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
        content='''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ac sodales felis. 
        '''
    ))

async def page2_1(q):
    add_card(q, 'chart1', ui.plot_card(
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
        plot=ui.plot([ui.mark(type='interval', x='=product', y='=price', color='=country', stack='auto',
                              dodge='=category', y_min=0)])
    ))

    add_card(q, 'chart2', ui.plot_card(
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
    ))

    add_card(q, 'table', ui.form_card(box='vertical', items=[ui.table(
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
    ]))

async def page3_1(q):
    add_card(q, 'show_dialog_card', 
        ui.form_card(box='horizontal', items=[
            ui.button(name='show_dialog', label='Open dialog', primary=True)
        ])
    )
    for i in range(8):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))

async def page4_1(q):
    add_card(q, 'form', ui.form_card(box='vertical', items=[
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1'),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox1', label='Textbox 1'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step2', label='Next', primary=True),
        ]),
    ]))

async def page4_2(q):
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]

async def page4_3(q):
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]

def example_dialog(q):
    q.page['meta'].dialog = ui.dialog(
        title='Hello!',
        name='my_dialog',
        items=[
            ui.text('Click the X button to close this dialog.'),
        ],
        # Enable a close button (displayed at the top-right of the dialog)
        closable=True,
        # Get notified when the dialog is dismissed.
        events=['dismissed'],
    )


