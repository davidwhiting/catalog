from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import logging

########################################################################
####################  STANDARD WAVE CARD FUNCTIONS  ####################
########################################################################

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q: Q, name: str, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

# Remove all the cards related to navigation.
def clear_cards(q: Q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)

################################################################
##################  ERROR CHECKING FUNCTIONS  ##################
################################################################

async def show_error(q: Q, error: str, page='debug') -> None:
    """
    Displays errors.
    """
    logging.error(error)

    # Clear all cards
    clear_cards(q)

    # Format and display the error
    q.page[page] = crash_report(q)

    await q.page.save()

def crash_report(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
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
        box='content',
        items=[
            ui.stats(items=[
                ui.stat(
                    label='',
                    value='Oops!',
                    caption='Something went wrong',
                    icon='Error'
                )
            ],),
            ui.separator(),
            ui.text_l(content='Apologies for the inconvenience!'),
            ui.buttons(items=[ui.button(name='reload', label='Reload', primary=True)]),
            ui.expander(name='report', label='Error Details', items=[
                ui.text(
                    f'To report this issue, please open an issue with the details below:'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )

async def reload(q: Q): 
    """
    Reset the client (browser tab).
    This function is called when the user clicks "Reload" on the crash report.
    """
    logging.info('Reloading client')
    q.client.initialized = False
    await initialize_client(q)

###############################################################################
## Adapted from Waveton, will need to rewrite
###############################################################################

def clear_cards_waveton(q: Q, card_names: List[str]) -> None:
    logging.info('Clearing cards')
    for card_name in card_names:
        del q.page[card_name]

async def handle_fallback_waveton(q: Q) -> None:
    logging.info('Adding fallback page')
    q.page['fallback'] = ui.form_card(box='fallback', items=[ui.text('Uh-oh, something went wrong!')])
    await q.page.save()

async def show_error_waveton(q: Q, error: str) -> None:
    logging.error(error)
    clear_cards_waveton(q, q.user.cards)
    q.page['error'] = crash_report_card(q)
    await q.page.save()
