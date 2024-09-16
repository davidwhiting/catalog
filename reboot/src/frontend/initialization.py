# initialization.py
from h2o_wave import Q
import logging
from frontend.cards import meta_card, header_card, footer_card, main_card

async def initialize_app(q: Q) -> None:
    logging.info('Initializing app')
    q.app.cards = ['main']
    q.app.initialized = True

async def initialize_client(q: Q) -> None:
    logging.info('Initializing client')
    q.page['meta'] = meta_card
    q.page['header'] = header_card
    q.page['footer'] = footer_card
    q.page['main'] = main_card
    q.client.initialized = True
    await q.page.save()
