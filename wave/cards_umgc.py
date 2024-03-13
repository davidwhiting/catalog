import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates

## A fallback card for handling bugs
#fallback = ui.form_card(
#    box='fallback',
#    items=[ui.text('Uh-oh, something went wrong!')]
#)

def select_semester(q, location='horizontal'):
    menu_width = '250px'
    return ui.form_card(
        box=location,
        items=[
            ui.dropdown(
                name='first', 
                label='Start Term', 
                value=q.args.start_term,
                trigger=True,
                width=menu_width,
                choices=[
                    ui.choice(label="Spring 2024"),
                    ui.choice(label="Summer 2024"),
                    ui.choice(label="Fall 2024"),
                    ui.choice(label="Winter 2025"),
                ]
            ),
        ]
    )

toggle = ui.form_card(box='rightgrid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

transfer_toggle = ui.form_card(box='grid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

markdown = ui.form_card(
    box='leftnote',
    items=[ui.text(templates.sample_markdown)]
)

#async def serve(q: Q):
#    if not q.client.initialized:
#        q.page['example'] = ui.form_card(box='1 1 2 3', items=[])
#        q.client.initialized = True
#    if 'profile' in q.args and not q.args.show_form:
#        q.page['example'].items = [
#            ui.text(f'profile={q.args.profile}'),
#            ui.text(f'preferences={q.args.preferences}'),
#            ui.text(f'logout={q.args.logout}'),
#            ui.button(name='show_form', label='Back', primary=True),
#        ]
#    else:
#        q.page['example'].items = [
#            ui.menu(image=image, items=commands),
#            ui.menu(icon='Add', items=commands),
#            ui.menu(label='App', items=commands),
#            ui.menu(items=commands)
#        ]
#    await q.page.save()

def step3(q):
        # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='student_reset', label='Finish', primary=True),
        ])
    ]


def stats(D):
    return ui.form_card(
        box='horizontal', items=[
            ui.stats(justify='between', items=[
                ui.stat(label='Credits', 
                        value=str(D['total_credits_remaining']), 
                        caption='Credits Remaining', 
                        icon='LearningTools'),            
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

