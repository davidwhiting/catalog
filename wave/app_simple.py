from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List

import json

script = '''
const
  width = 300,
  height = Math.min(640, width),
  groupTicks = (d, step) => {{
    const k = (d.endAngle - d.startAngle) / d.value;
    return d3.range(0, d.value, step).map(value => {{
      return {{ value: value, angle: value * k + d.startAngle }};
    }});
  }},
  formatValue = d3.formatPrefix(",.0", 1e3),
  chord = d3.chord()
    .padAngle(0.05)
    .sortSubgroups(d3.descending),
  outerRadius = Math.min(width, height) * 0.5 - 30,
  innerRadius = outerRadius - 20,
  arc = d3.arc()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius),
  ribbon = d3.ribbon()
    .radius(innerRadius),
  color = d3.scaleOrdinal()
    .domain(d3.range(4))
    .range(["#000000", "#FFDD89", "#957244", "#F26223"]),
  render = (data) => {{
    const svg = d3.select("#d3-chart")
      .append("svg")
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("font-size", 10)
      .attr("font-family", "sans-serif");

    const chords = chord(data);

    const group = svg.append("g")
      .selectAll("g")
      .data(chords.groups)
      .join("g");

    group.append("path")
      .attr("fill", d => color(d.index))
      .attr("stroke", d => d3.rgb(color(d.index)).darker())
      .attr("d", arc);

    const groupTick = group.append("g")
      .selectAll("g")
      .data(d => groupTicks(d, 1e3))
      .join("g")
      .attr("transform", d => `rotate(${{d.angle * 180 / Math.PI - 90}}) translate(${{outerRadius}},0)`);

    groupTick.append("line")
      .attr("stroke", "#000")
      .attr("x2", 6);

    groupTick
      .filter(d => d.value % 5e3 === 0)
      .append("text")
      .attr("x", 8)
      .attr("dy", ".35em")
      .attr("transform", d => d.angle > Math.PI ? "rotate(180) translate(-16)" : null)
      .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
      .text(d => formatValue(d.value));

    svg.append("g")
      .attr("fill-opacity", 0.67)
      .selectAll("path")
      .data(chords)
      .join("path")
      .attr("d", ribbon)
      .attr("fill", d => color(d.target.index))
      .attr("stroke", d => d3.rgb(color(d.target.index)).darker());
  }};

  render({data})
'''

data = [
    [11975, 5871, 8916, 2868],
    [1951, 10048, 2060, 6171],
    [8010, 16145, 8090, 8045],
    [1013, 990, 940, 6907],
]

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

    d3_content = '<div id="d3-chart" style="width:100%; height: 100%"></div>'

#    q.page['meta'] = ui.meta_card(
#        box='',
#        script=ui.inline_script(content=script.format(data=json.dumps(data)), requires=['d3']),
#        scripts=[ui.script(path='https://d3js.org/d3.v5.min.js')],
#        title='Test D3 Import',
#        theme='ember',
#        layouts=[
#            ui.layout(
#                breakpoint='xs',
#                min_height='100vh',
#                max_width='1200px',
#                zones=[
#                    ui.zone('header'),
#                    ui.zone('content', size='1', zones=[
#                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
#                        ui.zone('vertical', size='2', ),
#                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
#                    ]),
#                    ui.zone(name='footer'),
#                ]
#            )
#        ]
#    )
    q.page['meta'] = ui.meta_card(
        box='',
        script=ui.inline_script(content=script.format(data=json.dumps(data)), requires=['d3']),
        scripts=[ui.script(path='https://d3js.org/d3.v5.min.js')],
        title='Test D3 Import',
        theme='ember'
#        layouts=[
#            ui.layout(
#                breakpoint='xs',
#                min_height='100vh',
#                max_width='1200px',
#                zones=[
#                    ui.zone('header'),
#                    ui.zone('content', size='1', zones=[
#                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
#                        ui.zone('vertical', size='2', ),
#                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
#                    ]),
#                    ui.zone(name='footer'),
#                ]
#            )
#        ]
    )

    image_path, = await q.site.upload(['umgc-logo.png'])

    q.page['header'] = ui.header_card(
#        box='header',
        box='1 1 6 1',
        title='UMGC Curriculum Advisor',
        subtitle="[Title TBD]",
        image=image_path,
        items=[ui.menu(icon='', items=[ui.command(name='change_theme', icon='ClearNight', label='Dark Mode')])]
    )
#    q.page['footer'] = ui.footer_card(
#        box='footer',
#        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
#    )

    d3_width = '500px'

#    q.page['d3_example'] = ui.markup_card(
##        box=ui.box('vertical',size=0), 
#        box='5 5 6 6'
#        title='D3 Example', 
#        content=d3_content
#    )

    menu_width = '250px'
    
    q.page['controls'] = ui.form_card(
#        box='horizontal',
        box='1 3 10 2'
        items=[
            ui.dropdown(
                name='degree', 
                label='Degree', 
                value=q.args.degree,
                trigger=True,
#                width=menu_width,
                choices=[
                    ui.choice(name='AS', label="Associate"),
                    ui.choice(name='BS', label="Bachelor's"),
                    ui.choice(name='MS', label="Master's"),
                    ui.choice(name='DC', label="Doctorate"),
                    ui.choice(name='UC', label="Undergraduate Certificate"),
                    ui.choice(name='GC', label="Graduate Certificate")
            ])
#            ui.dropdown(
#                name='area_of_study', 
#                label='Area of Study', 
#                value=q.args.area_of_study,
#                trigger=False,
#                disabled=False,
#                width=menu_width,
#                choices=[
#                    ui.choice(name='BM', label='Business & Management'),
#                    ui.choice(name='CS', label='Cybersecurity'),
#                    ui.choice(name='DA', label='Data Analytics'),
#                    ui.choice(name='ET', label='Education & Teaching'),
#                    ui.choice(name='HS', label='Healthcare & Science'),
#                    ui.choice(name='LA', label='Liberal Arts & Communications'),
#                    ui.choice(name='PS', label='Public Safety'),
#                    ui.choice(name='IT', label='IT & Computer Science')
#            ]),
#            ui.dropdown(
#                name='major', 
#                label='Major', 
#                value=q.args.major,
#                trigger=False,
#                disabled=False,
#                width=menu_width,
#                choices=[
#                    ui.choice(name='AC', label='Accounting'),
#                    ui.choice(name='BA', label='Business Administration'),
#                    ui.choice(name='FI', label='Finance'),
#                    ui.choice(name='HR', label='Human Resource Management'),
#                    ui.choice(name='MS', label='Management Studies'),
#                    ui.choice(name='MK', label='Marketing'),
#            ]),
        ]
    )

#    add_card(q, 'courses_completed', ui.wide_gauge_stat_card(
#        box='horizontal',
#        title='Courses Completed',
#        value='={{intl foo minimum_fraction_digits=0 maximum_fraction_digits=0}}',
#        aux_value='={{intl bar style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
#        plot_color='$red',
#        progress=0.56,
#        data=dict(foo=123, bar=0.56)
#        ))
#    add_card(q, 'finish_date', ui.wide_gauge_stat_card(
#        box='horizontal',
#        title='Estimated Completion Date',
#        value='={{intl foo minimum_fraction_digits=0 maximum_fraction_digits=0}}',
#        aux_value='={{intl bar style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
#        plot_color='$red',
#        progress=0.56,
#        data=dict(foo=123, bar=0.56)
#        ))
#    add_card(q, 'speed', ui.tall_info_card(
#        box='horizontal', name='', title='Speed',
#        caption='The models are performant thanks to...', icon='SpeedHigh'
#        ))

#    await home(q)


#@on()
#async def home(q: Q):
#    clear_cards(q)
#    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))


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
