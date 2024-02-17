from h2o_wave import main, app, Q, site, ui, on, run_on
import json
import os.path

# The example D3 Javascript file is located in the same directory as this example; get its path
d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'plot_d3.js')

# Upload the script to the server. Typically, you'd do this only once, when your app is installed.
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
html = html_template.format(script_path=d3_js_script_path, data=json.dumps(data))

#page.save()

@app('/d3')
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
        title='My Wave App',
        theme='light',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='D3 Wave',
        subtitle="Example to get us started",
        image='https://wave.h2o.ai/img/h2o-logo.svg',
        items=[ui.menu(icon='', items=[ui.command(name='change_theme', icon='ClearNight', label='Dark Mode')])]
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )
    q.page['d3plot'] = ui.frame_card(
        box=ui.box('grid', height='600px', width='600px'),
        title='D3 Plot',
        content=html,
    )

    await home(q)
#page = site['/demo']
#q.page['example'] = ui.frame_card(
#    box='1 1 5 8',
#    title='D3 Chord Diagram',
#    content=html,
#)


@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))

#@on()
#async def change_theme(q: Q):
#    """Change the app from light to dark mode"""
#    if q.client.dark_mode:
#        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='ClearNight', label='Dark mode')])]
#        q.page["meta"].theme = "light"
#        q.client.dark_mode = False
#    else:
#        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='Sunny', label='Light mode')])]
#        q.page["meta"].theme = "h2o-dark"
#        q.client.dark_mode = True


# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
