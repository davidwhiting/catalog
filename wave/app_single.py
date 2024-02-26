from h2o_wave import main, app, Q, site, ui, on, run_on, data, graphics as g
from typing import Optional, List
import pandas as pd
import json
import os.path

import cards
import templates
import utils

### Note: This loading of the javascript file is not working for me for some reason.
###       It did work for the previous D3 example.
###       Debug later
## The example D3 Javascript file is located in the same directory as this example; get its path
##d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'plot_d3.js')
#d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'class_d3.js')
## Upload the script to the server. Typically, you'd do this only once, when your app is installed.
## (move this to the init section?)
#d3_js_script_path, = site.upload([d3_js_script_filename])

# Import the json file to a dataframe
# eventually we will extract this from the database

#df = pd.DataFrame(templates.data_json)

df = pd.DataFrame(templates.data_json_new)

# pick up start_term from the form
start_term = 'SPRING 2024'

df, headers = utils.prepare_d3_data(df, start_term.upper())

terms_remaining = max(headers.period)
completion_date = headers.loc[headers['period'] == terms_remaining, 'name'].values[0].capitalize()
total_credits_remaining = df['credits'].sum()
credits_next_term = headers.loc[headers['period'] == 1, 'credits'].values[0]

# Convert to json for passing along to our d3 function
#json_data = df.to_json(orient='records')

tuition = {
    'in_state': 324,
    'out_of_state': 499,
    'military': 250
}

cost_per_credit = tuition['military']
total_cost_remaining = "${:,}".format(total_credits_remaining * cost_per_credit)
next_term_cost = "${:,}".format(credits_next_term * cost_per_credit)

# Plug JSON-serialized data into our html template
# example_html = html_template_example.format(script_path=d3_js_script_path, data=json.dumps(example_data))


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
#        q.page['spinbox'] = ui.form_card(box='slider', items=utils.get_form_items(None))
#        q.client.initialized = True
#    if q.args.spinbox_trigger is not None:
#        q.page['spinbox'].items = utils.get_form_items(q.args.spinbox_trigger)

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
#        q.page['spinbox'] = ui.form_card(box='slider', items=utils.get_form_items(None))
#        q.client.initialized = True
#    if q.args.spinbox_trigger is not None:
#        q.page['spinbox'].items = utils.get_form_items(q.args.spinbox_trigger)

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
    df_json = df.to_json(orient='records')
    headers_json = headers.to_json(orient='records')

    html_template = templates.html_code_minimal.format(javascript=templates.javascript_minimal, 
                                                       headers=headers_json, data=df_json)
#    html_template = templates.html_code.format(javascript=d3_js_script_path, data=json_data)
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
        ui.stats(justify='between', 
            items=[
                ui.stat(
                    label='Tuition', 
                    value=next_term_cost, 
                    caption='Next Term Tuition', 
                    icon='Money'),
#            ], 
#            items=[
                ui.stat(
                    label='Credits', 
                    value=str(total_credits_remaining), 
                    caption='Credits Remaining', 
                    icon='Education'),            
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
            ]
        )
    ])

    q.page['markdown'] = cards.markdown

@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))

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
