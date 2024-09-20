import logging
from h2o_wave import main, app, Q, ui, on, run_on, data, expando_to_dict
from typing import Any, Dict, Callable, List, Optional, Union
import os
import pandas as pd
import numpy as np

import sys
import traceback

import frontend_classic as frontend
from frontend_classic import add_card, clear_cards, show_error, crash_report

import backend

# App name and repo URL for error reporting
app_name = 'My App'

@on('#page1')
async def page1(q: Q):
    await frontend.page1(q)

@on('#page2')
async def page2(q: Q):
    await frontend.page2(q)

@on('#page3')
async def page3(q: Q):
    await frontend.page3(q)

@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    await frontend.page4(q)

@on()
async def page4_step2(q: Q):
    await frontend.page4_step2(q)

@on()
async def page4_step3(q: Q):
    await frontend.page4_step3(q)

@on()
async def reload(q: Q): 
    await frontend.reload(q)
