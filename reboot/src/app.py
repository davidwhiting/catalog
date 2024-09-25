# File descriptions:
# - app.py: logic for the app
# - frontend/: components of the Wave UI
# - frontend/cards.py: card definitions used by frontend
# - frontend/utils: card placement functions
# - backend/: python and sql functions independent of UI
#
# To ensure no circular references:
# - app.py imports frontend and backend functions
#   - frontend functions import backend and each other
#   - backend functions do not import any frontend at all

from h2o_wave import (
    app,
    data,
    main,
    on,
    Q,
    run_on,
    ui
)
from typing import Optional, List
import logging

import frontend.serve
import frontend.pages as pages
import frontend.cards as cards

@on('#page1')
async def page1(q: Q):
    await pages.page1(q)

#######################################################
####################  HOME EVENTS  ####################
#######################################################

@on('#home')
@on('return_home')
async def home(q: Q):
    await pages.home(q)

@on()
async def next_demographic_1(q: Q):
    await pages.next_demographic_1(q)

@on()
async def next_demographic_2(q: Q):
    await pages.next_demographic_2(q)


##########################################################
####################  PROGRAM EVENTS  ####################
##########################################################

@on('#program')
async def program(q: Q):
    await pages.program(q)

##############################
###  Program Menu actions  ###
##############################

@on()
async def menu_degree(q: Q):
    await pages.menu_degree(q)

@on()
async def menu_area(q: Q):
    await pages.menu_area(q)

@on()
async def menu_program(q: Q):
    await pages.menu_program(q)


###############################
###  Program Table actions  ###
###############################

@on()
async def program_table(q: Q):
    await pages.program_table(q)

@on()
async def view_program_description(q: Q):
    await pages.view_program_description(q)

@on()
async def add_ge(q: Q):
    await pages.add_ge(q)

@on()
async def add_elective(q: Q):
    await pages.add_elective(q)

@on()
async def select_program(q: Q):
    await pages.select_program(q)

############################
## Dismiss dialog actions ##
############################

#@on('my_dialog.dismissed')
@on('schedule_table.dismissed')
@on('schedule_description_dialog.dismissed')
@on('program_table.dismissed')
@on('required_description_dialog.dismissed')
async def dismiss_dialog(q: Q):
    logging.info('Dismissing dialog')
    q.page['meta'].dialog = None
    await q.page.save()

#######################################################
####################  MAIN SERVER  ####################
#######################################################

@app('/', on_startup=frontend.serve.on_startup, on_shutdown=frontend.serve.on_shutdown)
async def serve(q: Q):
    await frontend.serve.serve_v2(q)
