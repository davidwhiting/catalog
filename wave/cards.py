import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates

# App name
app_name = 'UMGC Course Assistant'

## update to change to davidwhiting/catalog (updated from WaveTon)
## Link to repo. Report bugs/features here :)
repo_url = 'https://github.com/davidwhiting/catalog'
issue_url = f'{repo_url}/issues/new?assignees=davidwhiting&labels=bug&template=error-report.md&title=%5BERROR%5D'

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
# Layout has gotten too busy, perhaps simplify
meta = ui.meta_card(
    box='', 
    title='UMGC Wave App',
    theme='ember',
    layouts=[
        ui.layout(
            breakpoint='xs', 
            min_height='100vh', 
            zones=[
                ui.zone('header'),
                ui.zone('main'),   # delete after debugging
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. 
                    # Empty zones are ignored.
                    ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                    ui.zone('dashboard', direction=ui.ZoneDirection.ROW),
                    ui.zone('d3', direction=ui.ZoneDirection.ROW),
#                    ui.zone('display', zones=[
#                        ui.zone('display_left', width='80%'),
#                        ui.zone('display_right', width='20%')
#                    ]),
#                    ui.zone('dashboard2', direction=ui.ZoneDirection.ROW),
                    ui.zone('vertical'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                ]),
                ui.zone('error'), # for error reporting
                ui.zone(name='footer'),
            ]
        )
    ]
)

footer = ui.footer_card(
    box='footer',
    caption='''
Software prototype built by David Whiting using [H2O Wave](https://wave.h2o.ai). 
This app is in pre-alpha stage. Feedback welcomed.
    '''
)

def header(image_path, q):
    persona_image='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&h=750&w=1260'
    commands = [
        ui.command(name='profile', label='Profile', icon='Contact'),
        ui.command(name='preferences', label='Preferences', icon='Settings'),
        ui.command(name='logout', label='Logout', icon='SignOut'),
    ]

    result = ui.header_card(
        box='header', 
        title='UMGC Programs',
        subtitle="Registration Assistant",
        image=image_path,
        #icon='BuildQueue',
        #icon_color='black'
        secondary_items=[
            ui.tabs(name='tabs', value=f'#{q.args["#"]}' if q.args['#'] else '#home', link=True, items=[
                ui.tab(name='#home', label='Home'),
                ui.tab(name='#student', label='Student Info'),
                ui.tab(name='#major', label='Select Major'),
                ui.tab(name='#courses', label='Schedule Courses'),
                ui.tab(name='#electives', label='Electives'),
            ]),
        ],
        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)],
#        items=[ui.persona(title='John Doe', subtitle='Student', size='xs', image=persona_image)]
    )
    return result

def dropdown_menus(q):
    menu_width = '250px'
    return ui.form_card(
        box='horizontal',
        items=[
            ui.inline(
                items=[
                    ui.dropdown(
                        name='degree', 
                        label='Degree', 
                        value=q.client.degree if hasattr(q.client, 'degree') else q.args.degree,
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
                        value=q.client.area_of_study if hasattr(q.client, 'area_of_study') else q.args.area_of_study,
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
                        value=q.client.major if hasattr(q.client, 'major') else q.args.major,
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

def d3plot(html, location='horizontal'):
    result = ui.frame_card(
        box=ui.box(location, height='500px', width='100%'),
        title='Tentative Course Schedule',
        content=html
    )
    return result

# A fallback card for handling bugs (from WaveTon)
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)


# (from WaveTon)
def crash_report(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
    This function is called by the main serve() loop on uncaught exceptions.
    """

    def code_block(content): return '\n'.join(['```', *content, '```'])

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
                ui.text(
                    f'To report this issue, <a href="{issue_url}" target="_blank">please open an issue</a> with the details below:'),
                ui.text_l(content=f'Report Issue in App: **{app_name}**'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )
