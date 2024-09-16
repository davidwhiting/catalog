import logging
from h2o_wave import Q, ui
from typing import List
from frontend.cards import crash_report_card

def clear_cards(q: Q, card_names: List[str]) -> None:
    logging.info('Clearing cards')
    for card_name in card_names:
        del q.page[card_name]

async def handle_fallback(q: Q) -> None:
    logging.info('Adding fallback page')
    q.page['fallback'] = ui.form_card(box='fallback', items=[ui.text('Uh-oh, something went wrong!')])
    await q.page.save()

async def show_error(q: Q, error: str) -> None:
    logging.error(error)
    clear_cards(q, q.app.cards)
    q.page['error'] = crash_report_card(q)
    await q.page.save()
