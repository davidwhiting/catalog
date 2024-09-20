
from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List

import delete_me_new as dmn
from delete_me_new import add_card, clear_cards

import delete_me_frontend as fe

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

async def init(q: Q) -> None:
    q.page['meta'] = fe.meta_card
    q.page['sidebar'] = fe.return_sidebar(q)
    q.page['header'] = fe.header_card

    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)


@app('/')
async def serve(q: Q):
    # Run only once per client connection.
    if not q.client.initialized:
        q.client.cards = set()
        await init(q)
        q.client.initialized = True

    # Handle routing.
    await run_on(q)
    await q.page.save()

