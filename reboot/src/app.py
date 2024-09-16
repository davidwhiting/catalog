# app.py
from h2o_wave import Q, main, app, run_on, on, ui
from typing import List
import logging
import sys
#from error_handling import show_error, handle_fallback

## app.py can call frontend and backend
## frontend can ball backend
## backend should not call others
## This will prevent circular references

from frontend.initialization import initialize_app, initialize_client
from frontend.utils import clear_cards, handle_fallback, show_error
from frontend.cards import meta_card, header_card, footer_card, main_card, crash_report_card

logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

@app('/')
async def serve(q: Q) -> None:
    try:
        if not q.app.initialized:
            await initialize_app(q)
        if not q.client.initialized:
            await initialize_client(q)
        elif await run_on(q):
            pass

        # This condition should never execute unless there is a bug in our code
        # Adding this condition here helps us identify those cases (instead of seeing a blank page in the browser)
        else:
            await handle_fallback(q)

    except NameError as e:
        error_msg = f"NameError: {str(e)}. This usually means a variable or function is being used before it's defined."
        logging.error(error_msg)
        await show_error(q, error_msg)

    except ImportError as e:
        error_msg = f"ImportError: {str(e)}. This usually means a required module is missing."
        logging.error(error_msg)
        await show_error(q, error_msg)

    except SyntaxError as e:
        error_msg = f"SyntaxError: {str(e)}. This usually means there's a syntax error in the code."
        logging.error(error_msg)
        await show_error(q, error_msg)

    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"An unexpected {error_type} occurred: {str(e)}"
        logging.error(error_msg)
        await show_error(q, error_msg)

    finally:
        # This ensures that any changes to the page are saved, even if an error occurred
        await q.page.save()

@on('reload')
async def reload_client(q: Q) -> None:
    logging.info('Reloading client')
    clear_cards(q, ['main'])
    await initialize_client(q)
