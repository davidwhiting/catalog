## This file should contain cards but generally not place them.
## Thus, cards are either defined by a function (because they have to access Q)
## or they are an object themselves.

from h2o_wave import Q, ui, data, copy_expando, expando_to_dict
import traceback
import sys


########################################################
################  ERROR CHECKING CARDS  ################
########################################################

def crash_report_edited(q: Q) -> ui.FormCard:
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
                ui.text(f'To report this issue, please open an issue with the details below:'),
                ui.text_l(content=f'Report Issue in App'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )


## To delete later

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

