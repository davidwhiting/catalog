from h2o_wave import main, app, Q, site, ui, on, run_on, data, graphics as g
from typing import Optional, List
import pandas as pd
import json
import os.path

import cards

# The example D3 Javascript file is located in the same directory as this example; get its path
d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'plot_d3.js')

# Upload the script to the server. Typically, you'd do this only once, when your app is installed.
# move this to the init section?
d3_js_script_path, = site.upload([d3_js_script_filename])

data_json = [
    {
        "seq": 1,
        "name": "TEST 123",
        "credits": 5,
        "color": "purple",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1
    },
    {
        "seq": 2,
        "name": "LIBS 150",
        "credits": 1,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1
    },
    {
        "seq": 3,
        "name": "WRTG 111",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1
    },
    {
        "seq": 4,
        "name": "WRTG 112",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 5,
        "name": "NUTR 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 6,
        "name": "BMGT 110",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 7,
        "name": "SPCH 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 8,
        "name": "STAT 200",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 9,
        "name": "IFSM 300",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 10,
        "name": "ACCT 220",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 11,
        "name": "HUMN 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 12,
        "name": "BIOL 103",
        "credits": 4,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 5
    },
    {
        "seq": 13,
        "name": "ECON 201",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 14,
        "name": "ARTH 334",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 5
    },
    {
        "seq": 15,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 6
    },
    {
        "seq": 16,
        "name": "ECON 203",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 6
    },
    {
        "seq": 17,
        "name": "ACCT 221",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "ACCT 220",
        "period": 6
    },
    {
        "seq": 18,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 19,
        "name": "BMGT 364",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 20,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 21,
        "name": "BMGT 365",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "BMGT 364",
        "period": 8
    },
    {
        "seq": 22,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 8
    },
    {
        "seq": 23,
        "name": "MRKT 310",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 8
    },
    {
        "seq": 24,
        "name": "WRTG 394",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "WRTG 112",
        "period": 9
    },
    {
        "seq": 25,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 9
    },
    {
        "seq": 26,
        "name": "BMGT 380",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 9
    },
    {
        "seq": 27,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 28,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 29,
        "name": "HRMN 300",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 30,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 11
    },
    {
        "seq": 31,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 11
    },
    {
        "seq": 32,
        "name": "FINC 330",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "ACCT 221 & STAT 200",
        "period": 11
    },
    {
        "seq": 33,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 34,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 35,
        "name": "BMGT 496",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 36,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 37,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 38,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 39,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 14
    },
    {
        "seq": 40,
        "name": "BMGT 495",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "BMGT 365 & MRKT 310 & FINC 330",
        "period": 14
    },
    {
        "seq": 41,
        "name": "CAPSTONE",
        "credits": 1,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "FINC 330",
        "period": 14
    }
]

# Import the json file to a dataframe
# eventually we will extract this from the database
df = pd.DataFrame(data_json)

# Calculate these in the future from student selections
completion_date = 'Spring 2027'
terms_remaining = 14
total_credits_remaining = 120
# display instate or out-of-state status

tuition = {
    'in_state': 324,
    'out_of_state': 499,
    'military': 250
}

cost_per_credit = tuition['military']
credits_next_term = 7
total_cost_remaining = "${:,}".format(total_credits_remaining * cost_per_credit)
next_term_cost = "${:,}".format(credits_next_term * cost_per_credit)

# Plug JSON-serialized data into our html template
# example_html = html_template_example.format(script_path=d3_js_script_path, data=json.dumps(example_data))

def get_form_items(value: Optional[float]):
    return [
        ui.text(f'spinbox_trigger={value}'),
        ui.spinbox(name='spinbox_trigger', label='Credits', trigger=True),
    ]

@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True

    if q.args.show_inputs:
        q.page['sessions'].items = [
            ui.text(f'selected={q.args.checklist}'),
#            ui.button(name='show_form', label='Back', primary=True),
        ]
    else:
        q.page['example'] = ui.form_card(box='rightgrid', items=[
            ui.checklist(name='checklist', label='Sessions Attending',
                         choices=[ui.choice(name=x, label=x) for x in ['Session 1', 'Session 2', 'Session 3']]),
#            ui.button(name='show_inputs', label='Submit', primary=True),
        ])

#    # spinbox w/ trigger
#    if not q.client.initialized:
#        q.page['spinbox'] = ui.form_card(box='slider', items=get_form_items(None))
#        q.client.initialized = True
#    if q.args.spinbox_trigger is not None:
#        q.page['spinbox'].items = get_form_items(q.args.spinbox_trigger)

    if q.args.show_inputs:
        q.page['spinbox'].items = [
            ui.text(f'spinbox={q.args.spinbox}'),
#            ui.button(name='show_form', label='Back', primary=True),
        ]
    else:
        q.page['spinbox'] = ui.form_card(box='rightgrid', items=[
            ui.spinbox(name='spinbox', label='Courses per Session', min=1, max=3, step=1, value=1),
#            ui.button(name='show_inputs', label='Submit', primary=True),
        ])

#    # spinbox w/ trigger
#    if not q.client.initialized:
#        q.page['spinbox'] = ui.form_card(box='slider', items=get_form_items(None))
#        q.client.initialized = True
#    if q.args.spinbox_trigger is not None:
#        q.page['spinbox'].items = get_form_items(q.args.spinbox_trigger)

    # slider
    if q.args.show_inputs:
        q.page['slider'].items = [
            ui.text(f'slider={q.args.slider}'),
#            ui.button(name='show_form', label='Back', primary=True),
        ]
    else:
        q.page['slider'] = ui.form_card(box='rightgrid', items=[
            ui.slider(name='slider', label='Max Credits per Term', min=1, max=15, step=1, value=9),
#            ui.button(name='show_inputs', label='Submit', primary=True),
        ])

    # Other browser interactions
    await run_on(q)
    await q.page.save()

async def init(q: Q) -> None:
    q.client.cards = set()
    q.client.dark_mode = False
    q.page['meta'] = cards.meta

    image_path, = await q.site.upload(['umgc-logo.png'])
    q.page['header'] = cards.header(image_path)
    
    menu_width = '250px'
    # To do: Load menus from json

    q.page['dropdown_menus'] = ui.form_card(
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

    q.page['toggle'] = cards.toggle
    q.page['footer'] = cards.footer

    # Convert to json for passing along to our d3 function
    json_data = df.to_json(orient='records')
    html_template = cards.html_code.format(data=json_data)
    # Work on this later
#    html_template = cards.d3_template.format(script=cards.javascript_code, data=json_data)
    
    q.page['d3plot'] = cards.d3plot(html_template)

## Debug this sometime
#    stats_dict = {
#        "total_credits_remaining": total_credits_remaining, 
#        "next_term_cost": next_term_cost, 
#        "terms_remaining": terms_remaining, 
#        "completion_date": completion_date, 
#        "total_cost_remaining": total_cost_remaining     
#    }
#    q.page['stats'] = cards.stats(stats_dict)

    q.page['stats'] = ui.form_card(box='horizontal', items=[
        ui.stats(justify='between', items=[
            ui.stat(
                label='Credits', 
                value=str(total_credits_remaining), 
                caption='Credits Remaining', 
                icon='Education'),            
            ui.stat(
                label='Tuition', 
                value=next_term_cost, 
                caption='Estimated Tuition', 
                icon='Money'),
            ui.stat(
                label='Terms Remaining', 
                value=str(terms_remaining), 
                caption='Terms Remaining', 
                icon='Education'),
            ui.stat(
                label='Finish Date', 
                value=completion_date, 
                caption='(Estimated)', 
                icon='SpecialEvent'),
            ui.stat(
                label='Total Tuition', 
                value=total_cost_remaining, 
                caption='Estimated Tuition', 
                icon='Money'),
        ])
    ])

    q.page['markdown'] = cards.markdown

@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))

# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
