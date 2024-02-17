from h2o_wave import main, app, Q, site, ui, on, run_on, data
from typing import Optional, List
import json
import os.path

# The example D3 Javascript file is located in the same directory as this example; get its path
d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'plot_d3.js')

# Upload the script to the server. Typically, you'd do this only once, when your app is installed.
# move this to the init section?
d3_js_script_path, = site.upload([d3_js_script_filename])

html_template = '''
<!DOCTYPE html>
<html>
<head>
  <script src="https://d3js.org/d3.v5.js"></script>
</head>
<body style="margin:0; padding:0">
  <script src="{script_path}"></script>
  <script>render({data})</script>
</body>
</html>
'''

# This data is hard-coded here for simplicity.
# During production use, this data would be the output of some compute routine.
data = [
    [11975, 5871, 8916, 2868],
    [1951, 10048, 2060, 6171],
    [8010, 16145, 8090, 8045],
    [1013, 990, 940, 6907],
]

# Plug JSON-serialized data into our html template
html1 = html_template.format(script_path=d3_js_script_path, data=json.dumps(data))

@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True

    # Other browser interactions
    await run_on(q)
    await q.page.save()


async def init(q: Q) -> None:
    q.client.cards = set()
    q.client.dark_mode = False

    q.page['meta'] = ui.meta_card(
        box='',
        title='UMGC Wave App',
        theme='ember',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
#                max_width='1200px',
                max_width='100vw',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW, justify='center'),
                        ui.zone('horizontal2', direction=ui.ZoneDirection.ROW, size='1', 
                            zones=[
                               ui.zone('left1',  size='25%', direction=ui.ZoneDirection.COLUMN),
                               ui.zone('left2',  size='25%', direction=ui.ZoneDirection.COLUMN),
                               ui.zone('right1', size='49%', direction=ui.ZoneDirection.COLUMN),
                               ui.zone('right2', size= '1%', direction=ui.ZoneDirection.COLUMN),
                        ]),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center', 
                            zones=[
                               ui.zone('leftgrid',  size='5%'),
                               ui.zone('midgrid', size='90%'),
                               ui.zone('rightgrid',  size='5%'),
                       ]),
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )

    image_path, = await q.site.upload(['umgc-logo.png'])
    q.page['header'] = ui.header_card(
        box='header',
        title='UMGC Curriculum Assistant',
        subtitle="Title TBD",
        image=image_path,
        items=[ui.menu(icon='', items=[ui.command(name='change_theme', icon='ClearNight', label='Dark Mode')])]
    )
    
    menu_width = '250px'
    # To do: Load menus from json

    q.page['controls'] = ui.form_card(
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
    q.page['textbox'] = ui.form_card(
        box='left1',
        items=[ui.textbox(name='textbox_default', label='Student Name', 
                          value='John Doe', disabled=True)]
    )
    q.page['toggle'] = ui.form_card(box='horizontal', items=[
        ui.toggle(name='toggle', label='Toggle', value=True, disabled=True),
    ])
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )
    q.page['d3plot'] = ui.frame_card(
        box=ui.box('midgrid', height='600px', width='600px'),
        title='D3 Plot',
        content=html1,
    )

    q.page['graduation_year'] = ui.tall_gauge_stat_card(
        box=ui.box('left1', height='150px',),
        title='Credits',
        value='={{intl foo minimum_fraction_digits=0 maximum_fraction_digits=0}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$blue',
        progress=0.56,
        data=dict(foo=123, bar=0.56),
    )
    q.page['stats'] = ui.form_card(box='right1', items=[
        ui.stats(justify='between', items=[
            ui.stat(label='Category 1', value='$ 123.22', caption='Caption 1', icon='Home'),
            ui.stat(label='Category 2', value='$ 213.45', caption='Caption 2', icon='Cake'),
            ui.stat(label='Category 3', value='$ 963.12', caption='Caption 3', icon='Heart'),
        ])
    ])
    q.page['graduation_year2'] = ui.wide_gauge_stat_card(
        box=ui.box('right1', height='100px',),
        title='Finish Date',
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$red',
        progress=0.56,
        data=dict(foo=123, bar=0.56),
    )

    q.page['graduation_year4'] = ui.wide_bar_stat_card(
        box=ui.box('left1', 
#                   height='100px',),
                   size='1',),
        title='Finish Date',
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$green',
        progress=0.56,
        data=dict(foo=123, bar=0.56),
    )

    q.page['tall_stats'] = ui.tall_stats_card(
#        box=ui.box('right2', height='200px',),
        box=ui.box('left2'),
        items=[
            ui.stat(label='PARAMETER NAME', value='125%'),
            ui.stat(label='PARAMETER NAME', value='578 Users'),
            ui.stat(label='PARAMETER NAME', value='25K')
        ]
    )

@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))


@on()
async def change_theme(q: Q):
    """Change the app from light to dark mode"""
    if q.client.dark_mode:
        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='ClearNight', label='Dark mode')])]
        q.page["meta"].theme = "ember"
        q.client.dark_mode = False
    else:
        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='Sunny', label='Light mode')])]
        q.page["meta"].theme = "ember"
        q.client.dark_mode = True


# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
