
from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List

import frontend.utils

import delete_me_new as dmn
import delete_me_frontend as dmfe

from frontend.utils import add_card, clear_cards

@on('#page1')
async def page1(q: Q):
    await dmn.page1(q)

@on('#page2')
async def page2(q: Q):
    await dmn.page2(q)

@on('#page3')
async def page3(q: Q):
    await dmn.page3(q)

@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    await dmn.page4(q)

@on()
async def page4_step2(q: Q):
    await dmn.page4_step2(q)

@on()
async def page4_step3(q: Q):
    await dmn.page4_step3(q)

@app('/')
async def serve(q: Q):
    await frontend.utils.serve_v2(q)
