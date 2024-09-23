import logging
from h2o_wave import Q, ui
from typing import List, Optional
from frontend.cards import crash_report_card

###############################################################################
#############  Functions for on_startup() and on_shutdown() ###################
###############################################################################

async def on_startup() -> None:
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

async def on_shutdown() -> None:
    # Create shutdown actions if needed
    pass

######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

## Note: Changed all q.client to q.user because of mode='multicast' option in the @app decorator 

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q: Q, name: str, card: any) -> None:
    q.user.cards.add(name)
    q.page[name] = card

# Remove all the cards related to navigation.
def clear_cards(q: Q, ignore: Optional[List[str]] = []) -> None:
    if not q.user.cards:
        return
    for name in q.user.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.user.cards.remove(name)


###############################################################################
## Adapted from Waveton, will need to rewrite
###############################################################################

def clear_cards_waveton(q: Q, card_names: List[str]) -> None:
    logging.info('Clearing cards')
    for card_name in card_names:
        del q.page[card_name]

async def handle_fallback(q: Q) -> None:
    logging.info('Adding fallback page')
    q.page['fallback'] = ui.form_card(box='fallback', items=[ui.text('Uh-oh, something went wrong!')])
    await q.page.save()

async def show_error_waveton(q: Q, error: str) -> None:
    logging.error(error)
    clear_cards_waveton(q, q.user.cards)
    q.page['error'] = crash_report_card(q)
    await q.page.save()
