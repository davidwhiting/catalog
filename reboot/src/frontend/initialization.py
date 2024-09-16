# initialization.py
from h2o_wave import Q
import logging
from frontend.cards import meta_card, header_card, footer_card, main_card

###############################################################################
####################  Initialize app, user, client Functions ##################
###############################################################################

# need to be updated

async def initialize_app(q: Q) -> None:
    """
    Initialize the app. Code here is run once at the app level.
    """
    logging.info('Initializing app')
    q.app.initialized = True

    # show debug info and cards
    q.app.debug = True
 
    ## upload logo
    q.app.umgc_logo, = await q.site.upload(['umgc-logo-white.png'])

    # set global default first term
    q.app.default_first_term = 'Spring 2024'

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

async def initialize_app_waveton(q: Q) -> None:
    logging.info('Initializing app')
    q.app.cards = ['main'] # move to q.user.cards?
    q.app.initialized = True

async def initialize_client_waveton(q: Q) -> None:
    logging.info('Initializing client')
    q.page['meta'] = meta_card
    q.page['header'] = header_card
    q.page['footer'] = footer_card
    q.page['main'] = main_card
    q.client.initialized = True
    await q.page.save()
