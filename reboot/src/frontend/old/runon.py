import logging
from h2o_wave import Q, ui, run_on, on
from typing import List, Optional
from frontend.cards import crash_report_card

from frontend.initialization import initialize_app, initialize_client_waveton
from frontend.utils import clear_cards_waveton, handle_fallback
from frontend.utils import show_error_waveton as show_error


#################################################
#############  MAIN SERVE APP ###################
#################################################

async def serve(q: Q) -> None:
    """
    Main entry point. All queries pass through this function.
    """
    try:
        # Initialize the app if not already
        if not q.app.initialized:
            await initialize_app(q)

        ## Initialize the user if not already
        #if not q.user.initialized:
        #    await initialize_user(q)
        #    logging.info('Initializing user')

        # Initialize the client if not already
        if not q.client.initialized:
            await initialize_client_waveton(q)
            logging.info('Initializing client')

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

    await q.page.save()

###########################################################
##################  END SERVE FUNCTIONS  ##################
###########################################################


###############################################################################
#############  Functions for on_startup() and on_shutdown() ###################
###############################################################################
