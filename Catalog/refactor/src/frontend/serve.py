from h2o_wave import app, data, main, on, Q, run_on, ui
from typing import Optional, List
import logging

import backend.connection
import backend.student
import frontend.pages as pages
import frontend.cards as cards

#################################################################
#############  ON_STARTUP() AND ON_SHUTDOWN() ###################
#################################################################

async def on_startup() -> None:
    # Set up logging
    logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', 
                        level=logging.INFO)

async def on_shutdown() -> None:
    # Create shutdown actions if needed
    pass

#######################################################
#############  INITIALIZE FUNCTIONS ###################
#######################################################

async def initialize_app(q: Q, first_term: str = 'Spring 2024') -> None:
    """
    Initialize the app. Code here is run once at the app level.
    """
    logging.info('Initializing app')
    q.app.initialized = True

    # show debug info and cards
    q.app.debug = True
 
    ## upload logo
    q.app.logo, = await q.site.upload(['frontend/umgc-logo-white.png'])

    # set global default first term
    q.app.default_first_term = first_term

    # from waveton... include here or in q.user.cards or q.client.cards?
    #q.app.cards = ['main'] # move to q.user.cards?

    # SHORTCUT: Added these into the view directly, will fix this code later
    # as we fix the logic for these, will remove from disabled

    q.app.disabled_program_menu_items = {
        'Applied Technology',
        'Biotechnology',
        'Cybersecurity Technology',
        'East Asian Studies',
        'English',
        'General Studies',
        'History',
        'Laboratory Management',
        'Nursing for Registered Nurses',
        'Social Science',
        'Web and Digital Design',        
    }
    await q.page.save()

async def initialize_user(q: Q) -> None:
    """
    Initialize the user.

    - When in production with SSO, keep database connections at the user level
      rather than app (once per program run) or client (once per browser tab).
    - multicast mode will allow multiple users to connect simultaneously
    - In development, these will be at the client level. [Change all q.client here to q.user.]
    """
    logging.info('Initializing user')
    q.user.initialized = True

    await q.page.save()

async def initialize_client(q: Q) -> None:
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    home = '#home'
    # Mark as initialized at the client (browser tab) level
    q.client.initialized = True

    #### Move q.client to q.user if using multicast and sso
    #### (do this in production)
    conn = backend.connection.TimedSQLiteConnection('UMGC.db')
    q.client.conn = conn
    logging.info(f'sqlite connection: {q.client.conn}')

    # reset student
    client = backend.student.reset_student()
    q.client.student_info = client['student_info']
    logging.info(f'q.client.student_info debug: {q.client.student_info}')

    q.client.student_data = client['student_data']
    logging.info(f'q.client.student_data debug: {q.client.student_data}')

    q.client.role = 'student' # other option is admin/coach

    # Note: All user variables related to students will be saved in a dictionary
    # q.client.student_info
    #
    # This will allow us to keep track of student information whether the role is admin/coach 
    # (where we can easily switch students by deleting q.client.student_info and starting over), or
    # student roles (with single instance of q.client.student_info).
    #
    # For example, if q.client.user_id=2 is a coach working on a student with user_id=3, then we
    # populate q.client.student_info['user_id']=3 with that student's information.
    #
    # Student information stored in q.client.student_info
    #   - role in ('admin', 'coach') will start from new student or populate with saved
    #     student info using 'select student' dropdown menu (later will be lookup)
    #   - role == 'student' will start new or from saved student info from database

    student_user_id = 3 # new student... shortcut
    student_user_id = 7 # student with schedule created

    # populate q.client.student_info and q.client.student_data
    await backend.student.populate_student_info_data(q, student_user_id)

    #logging.info(f'q.client debug: {q.client}')

    q.client.cards = set()
    q.page['meta'] = cards.meta_card
    q.page['sidebar'] = cards.sidebar_card(q, home=home)
    q.page['header'] = cards.header_card
    q.page['footer'] = cards.footer_card
    logging.info(f"set q.page['footer']")
    logging.info(f"{q.args}")

    # If no active hash present, render home.
    if q.args['#'] is None:
        logging.info(f"q.args['#'] is None")
        await pages.home(q)
    else:
        logging.info(f"q.args['#'] is not None")

    await q.page.save()

#################################################
#############  MAIN SERVE APP ###################
#################################################

async def serve_v2(q: Q) -> None:
    """
    Main entry point. All queries pass through this function.
    """
    try:

        # Initialize the app if not already
        if not q.app.initialized:
            await initialize_app(q)

        # Initialize the user if not already
        if not q.user.initialized:
            await initialize_user(q)

        # Initialize the client if not already
        if not q.client.initialized:
            await initialize_client(q)

        logging.info('Made it through the initialize_client')
        # Handle routing.
        await run_on(q)

    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"An unexpected {error_type} occurred: {str(e)}"
        logging.error(error_msg)
        #await show_error(q, error_msg)

    await q.page.save()

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
