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

from h2o_wave import app, data, main, on, Q, run_on, ui
from typing import Optional, List
import logging

import frontend.serve
import frontend.pages as pages
import frontend.cards as cards

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

#########################################################
####################  SKILLS EVENTS  ####################
#########################################################

@on('#skills')
async def skills(q: Q):
    await pages.skills(q)

@on()
async def submit_skills_menu(q: Q):
    await pages.submit_skills_menu(q)

@on()
async def program_skills_table(q: Q):
    await pages.program_skills_table(q)

@on()
async def explore_skills_program(q: Q):
    await pages.explore_skills_program(q)

@on()
async def select_skills_program(q: Q):
    await pages.select_skills_program(q)

#########################################################
####################  COURSE EVENTS  ####################
#########################################################

@on('#courses')
async def courses(q: Q):
    await pages.courses(q)

#####################################################
####################  GE EVENTS  ####################
#####################################################

@on('#ge')
@on('goto_ge')
async def ge(q: Q):
    await pages.ge(q)
    await q.page.save()

#############
## GE Arts ##  
#############

@on()
async def ge_arts_check(q: Q):
    await pages.ge_arts_check(q)

@on()
async def ge_arts_1(q: Q):
    await pages.ge_arts_1(q)

@on()
async def ge_arts_2(q: Q):
    await pages.ge_arts_2(q)

############
## GE Beh ##
############

@on()
async def ge_beh_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['beh']['nopre'] = True
    await q.page.save()

@on()
async def ge_beh_1(q: Q):
    q.client.student_info['ge']['beh']['1'] = q.args.ge_beh_1
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_beh_2(q: Q):
    q.client.student_info['ge']['beh']['2'] = q.args.ge_beh_2
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Bio ##
############

@on()
async def ge_bio_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['bio']['nopre'] = True
    await q.page.save()

async def handle_dropdown_change(q, changed_dropdown):
    '''
    When one of three menus is selected, clear the others and reset 
    to defaults
    '''
    dropdowns=['ge_bio_1a', 'ge_bio_1b', 'ge_bio_1c']
    dropdowns.remove(changed_dropdown)

    selected = changed_dropdown.split('_')[2]
    q.client.student_info['ge']['bio'][selected] = q.args[changed_dropdown]

    for dropdown in dropdowns:
        # reset menu options to default
        q.page['ge_req4'].items[dropdown].value = None
        # clear q.client.student_info['ge']['bio'][which]
        which = dropdown.split('_')[2]
        q.client.student_info['ge']['bio'][which] = None

    await q.page.save()

@on()
async def ge_bio_1a(q: Q):
    logging.info('The value of ge_bio_1a = ' + q.args.ge_bio_1a)
#    await handle_dropdown_change(q, 'ge_bio_1a')
#    q.page['ge_debug'].content = ge_debug_content
#    await q.page.save()

    q.client.student_info['ge']['bio']['1a'] = q.args.ge_bio_1a
    q.client.student_info['ge']['bio']['1b'] = None
    q.client.student_info['ge']['bio']['1c'] = None
    # reset dropdown menu items?
    #q.page['ge_bio'].

    #q.page['ge_debug'].content = ge_debug_content(q)

    await q.page.save()

@on()
async def ge_bio_1b(q: Q):
    logging.info('The value of ge_bio_1b = ' + q.args.ge_bio_1b)
##    await handle_dropdown_change(q, 'ge_bio_1b')
##    q.page['ge_debug'].content = ge_debug_content
##    await q.page.save()
#   
    q.client.student_info['ge']['bio']['1a'] = None
    q.client.student_info['ge']['bio']['1b'] = q.args.ge_bio_1b
    q.client.student_info['ge']['bio']['1c'] = None
##    # reset dropdown menu items?

    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_bio_1c(q: Q):
    logging.info('The value of ge_bio_1c = ' + q.args.ge_bio_1c)
#    await handle_dropdown_change(q, 'ge_bio_1b')
#    q.page['ge_debug'].content = ge_debug_content
#    await q.page.save()

    q.client.student_info['ge']['bio']['1a'] = None
    q.client.student_info['ge']['bio']['1b'] = None
    q.client.student_info['ge']['bio']['1c'] = q.args.ge_bio_1c
#    # reset dropdown menu items?

    #q.page['ge_debug'].content = ge_debug_content
    await q.page.save()

@on()
async def ge_bio_2(q: Q):
    q.client.student_info['ge']['bio']['2'] = q.args.ge_bio_2
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#############
## GE Comm ##  These all work !!!
#############

@on()
async def ge_comm_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['comm']['nopre'] = True
    await q.page.save()

@on()
async def ge_comm_1(q: Q):
    q.client.student_info['ge']['comm']['1'] = q.args.ge_comm_1
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_comm_2(q: Q):
    q.client.student_info['ge']['comm']['2'] = q.args.ge_comm_2
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_comm_3(q: Q):
    q.client.student_info['ge']['comm']['3'] = q.args.ge_comm_3
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_comm_4(q: Q):
    q.client.student_info['ge']['comm']['4'] = q.args.ge_comm_4
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#############
## GE Math ##  This works! 
#############

@on()
async def ge_math_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['math']['nopre'] = True
    await q.page.save()

@on()
async def ge_math_1(q: Q):
    q.client.student_info['ge']['math']['1'] = q.args.ge_math_1
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Res ##
############

@on()
async def ge_res_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['res']['nopre'] = True
    await q.page.save()

@on()
async def ge_res_1(q: Q):
    q.client.student_info['ge']['res']['1'] = q.args.ge_res_1
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_2(q: Q):
    q.client.student_info['ge']['res']['2'] = q.args.ge_res_2
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_3(q: Q):
    q.client.student_info['ge']['res']['3'] = q.args.ge_res_3
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

@on()
async def ge_res_3a(q: Q):
    await pages.ge_res_3a(q)

@on()
async def ge_res_3b(q: Q):
    await pages.ge_res_3b(q)

@on()
async def ge_res_3c(q: Q):
    await pages.ge_res_3c(q)

############################################################
####################  ELECTIVES EVENTS  ####################
############################################################

@on('#electives')
async def electives(q: Q):
    pass
    #await q.page.save()

    #await pages.schedule(q)


############################################################
####################  SCHEDULES EVENTS  ####################
############################################################

@on('#schedule')
async def schedule(q: Q):
    await pages.schedule(q)

###########################
## Schedule Menu actions ##
###########################

@on()
async def submit_schedule_menu(q: Q):
    await pages.submit_schedule_menu(q)

############################
## Schedule Table actions ##
############################

@on()
async def schedule_table(q: Q):
    await pages.schedule_table(q)

# view description
@on()
async def view_schedule_description(q: Q):
    await pages.view_schedule_description(q)

# move class
@on()
async def move_class(q: Q):
    await pages.move_class(q)

# lock class
@on()
async def lock_class(q: Q):
    await pages.lock_class(q)

# select elective
@on()
async def select_elective(q: Q):
    await pages.select_elective(q)


#######################################################
####################  MISC EVENTS  ####################
#######################################################

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
