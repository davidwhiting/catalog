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

from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List

import frontend.serve
import frontend.pages as pages

@on('#page1')
async def page1(q: Q):
    await pages.page1(q)

#@on('#page2')
#async def page2(q: Q):
#    await dmn.page2(q)
#
#@on('#page3')
#async def page3(q: Q):
#    await dmn.page3(q)
#
#@on('#page4')
#@on('page4_reset')
#async def page4(q: Q):
#    await dmn.page4(q)
#
#@on()
#async def page4_step2(q: Q):
#    await dmn.page4_step2(q)
#
#@on()
#async def page4_step3(q: Q):
#    await dmn.page4_step3(q)

@app('/', on_startup=frontend.serve.on_startup, on_shutdown=frontend.serve.on_shutdown)
async def serve(q: Q):
    await frontend.serve.serve_v2(q)
