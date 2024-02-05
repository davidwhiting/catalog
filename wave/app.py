from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List

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

@on('#page1')
async def page1(q: Q):
    q.page['sidebar'].value = '#page1'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    menu_width = '250px'

    # To do: 
    # Load menus from json

    q.page['controls'] = ui.form_card(
        box='horizontal',
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

#    # Enable the dropdown menus if a value is selected in the previous dropdown.
#    if q.args.degree:
#        q.page['controls'].items[1].disabled = False
#    if q.args.area_of_study:
#        q.page['controls'].items[2].disabled = False

    for i in range(3):
        add_card(q, f'info{i}', ui.tall_info_card(box='horizontal', name='', title='Speed',
                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='600px'), title='How does magic work',
        image='https://images.pexels.com/photos/624015/pexels-photo-624015.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
        content='''
Lorem ipsum dolor sit amet,         '''
        )
    )

## Debug later, this should work but isn't
## Look at 
## https://github.com/h2oai/wave/discussions/1390 and
## https://github.com/h2oai/wave/issues/1884
    
@on('degree')
async def update_area_of_study(q: Q):
    q.page['controls'].items[1].disabled = False
    await q.page.save()


#    add_card(q, f'info{2}', ui.tall_info_card(box='horizontal', name='', title='Speed',
#                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))

## Below: Example of including d3 script on page.
## Replace the article preview card with this
## 

##import json
##import os.path
##from h2o_wave import site, ui
##
### The example D3 Javascript file is located in the same directory as this example; get its path
##d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'plot_d3.js')
##
### Upload the script to the server. Typically, you'd do this only once, when your app is installed.
##d3_js_script_path, = site.upload([d3_js_script_filename])
##
##html_template = '''
##<!DOCTYPE html>
##<html>
##<head>
##  <script src="https://d3js.org/d3.v5.min.js"></script>
##</head>
##<body style="margin:0; padding:0">
##  <script src="{script_path}"></script>
##  <script>render({data})</script>
##</body>
##</html>
##'''
##
### This data is hard-coded here for simplicity.
### During production use, this data would be the output of some compute routine.
##data = [
##    [11975, 5871, 8916, 2868],
##    [1951, 10048, 2060, 6171],
##    [8010, 16145, 8090, 8045],
##    [1013, 990, 940, 6907],
##]
##
### Plug JSON-serialized data into our html template
##html = html_template.format(script_path=d3_js_script_path, data=json.dumps(data))
##
##page = site['/demo']
##page['example'] = ui.frame_card(
##    box='1 1 5 8',
##    title='D3 Chord Diagram',
##    content=html,
##)
##page.save()

@on('#page2')
async def page2(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
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


@on('#page3')
async def page3(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(12):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))


@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    q.page['sidebar'].value = '#page4'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # If first time on this page, create the card.
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


@on()
async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
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


@on()
async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
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

# Themes: 
# ember
# benext
# lighting
# solarized
# winter-is-coming

async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', theme='ember', layouts=[ui.layout(
        breakpoint='xs', min_height='100vh', 
        zones=[
            ui.zone('header'),
            ui.zone('content', 
            zones=[
            # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                ui.zone('vertical'),
                ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
        ]),
    ])])
    image_path, = await q.site.upload(['umgc-logo.png'])

    q.page['header'] = ui.header_card(
        box='header', title='UMGC Curriculum Advisor', subtitle="Title TBD",
#        icon='World',
        image=image_path,
#        color='transparent',
#        color='card',
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#page1', link=True, items=[
                ui.tab(name='#page1', label='Home'),
                ui.tab(name='#page2', label='Charts'),
                ui.tab(name='#page3', label='Grid'),
                ui.tab(name='#page4', label='Form'),
            ]),
        ],
        items=[
            ui.textbox(name='search', icon='Search', width='200px', placeholder='Search...')
        ]
    )
    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)

@app('/')
async def serve(q: Q):
    # Run only once per client connection.
    if not q.client.initialized:
        q.client.cards = set()
        await init(q)
        q.client.initialized = True

    # Handle routing.
    await run_on(q)

#    # Enable the dropdown menus if a value is selected in the previous dropdown.
#    # Reference the page explicitly
#    if q.args['#'] == '#page1':
#        if q.args.degree:
#            q.page['controls'].items[1].disabled = False
#        if q.args.area_of_study:
#            q.page['controls'].items[2].disabled = False

    await q.page.save()