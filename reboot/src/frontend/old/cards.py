from h2o_wave import Q, main, app, run_on, on, expando_to_dict, ui

from backend.constants import APP_NAME as app_name
from backend.constants import REPO_URL as repo_url
from backend.constants import ISSUE_URL as issue_url

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information

# The header shown on all the app's pages

# The footer shown on all the app's pages

# Additional cards for the app's pages
main_card = ui.form_card(
    box='main',
    items=[
        ui.text('This is a great starting point to build an app.')
    ]
)

# A fallback card for handling bugs
fallback_card = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

def crash_report_card(q: Q) -> ui.FormCard:
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
                ui.text(
                    f'To report this issue, <a href="{issue_url}" target="_blank">please open an issue</a> with the details below:'),
                ui.text_l(content=f'Report Issue in App: **{app_name}**'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )
