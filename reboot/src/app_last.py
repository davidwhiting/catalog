# app.py
import frontend.runon
from h2o_wave import Q, main, app, run_on, on, ui
from typing import List
import logging
import sys
#from error_handling import show_error, handle_fallback

## app.py can call frontend and backend
## frontend can ball backend
## backend should not call others
## This will prevent circular references

from frontend.initialization import initialize_app, initialize_client_waveton
#initialize_user, 
#initialize_client
import frontend
from frontend.utils import clear_cards_waveton, handle_fallback, on_startup, on_shutdown
from frontend.utils import show_error_waveton as show_error

from frontend.cards import meta_card, header_card, footer_card, main_card, crash_report_card

logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

@app('/', on_startup=on_startup, on_shutdown=on_shutdown)
async def serve(q: Q) -> None:
    """
    Main entry point. All queries pass through this function.
    """
    await frontend.runon.serve(q)


# fix this to be reload from error
@on('reload')
async def reload_waveton(q: Q) -> None:
    logging.info('Reloading client')
    clear_cards_waveton(q, ['main'])
    await initialize_client_waveton(q)

from frontend.delete_me import page1, page2, page3, page4

@on('#page1')
async def page1(q: Q):
    await page1(q)

@on('#page2')
async def page2(q: Q):
    await page2(q)

@on('#page3')
async def page3(q: Q):
    await page3(q)

@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    await page4(q)

#@on()
#async def page4_step2(q: Q):
#    await frontend.page4_step2(q)
#
#@on()
#async def page4_step3(q: Q):
#    await frontend.page4_step3(q)
