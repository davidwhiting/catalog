from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import logging

from backend.queries import degree_query, area_query, program_query, program_query_old 
from backend.student import get_choices, initialize_ge, get_program_title, get_required_program_courses
from frontend.utils import add_card, clear_cards
import frontend.cards as cards

#################################################################
#################  EVENT AND HANDLER FUNCTIONS  #################
#################################################################

def course_description_dialog(q, course, which='schedule'):
    '''
    Create a dialog for the course description for a table.
    This will be used for multiple tables on multiple pages.
    course: indicate what course it's for
    df: DataFrame that the table was created from

    to do: course in the schedule df is called 'name'
           course is called course in the required df
           should simplify by changing schedule df to course AFTER
           updating d3 javascript code, since it's expecting name
    '''
    if which in ['required', 'schedule']:
        #df = q.client.student_data[which]
        if which == 'schedule':
            # make sure that schedule is a df instead of a dictionary
            # if dictionary, convert to df
            df = q.client.student_data['schedule']
            description = df.loc[df['name'] == course, 'description'].iloc[0]
   
        elif which == 'required':
            df = q.client.student_data['required']
            description = df.loc[df['course'] == course, 'description'].iloc[0]

        #description = df.loc[df['course'] == course, 'description'].iloc[0]

        q.page['meta'].dialog = ui.dialog(
            name = which + '_description_dialog',
            title = course + ' Course Description',
            width = '480px',
            items = [ui.text(description)],
            # Enable a close button
            closable = True,
            # Get notified when the dialog is dismissed.
            events = ['dismissed']
        )
    else:
        pass

#####################################################
####################  HOME PAGE  ####################
#####################################################

async def home(q: Q):
    q.page['sidebar'].value = '#home'
    clear_cards(q, ['demographics'])
    card_height = '400px'

    card = cards.return_task1_card(location='horizontal', width='350px')
    add_card(q, 'home/task1', card=card)

    card = cards.return_demographics_card(location='horizontal', width='400px')
    add_card(q, 'demographics', card)

    card = cards.return_tasks_card(checked=0, location='horizontal', width='350px', height=card_height)
    add_card(q, 'home/tasks', card)

    logging.info(f"Home: q.client is {q.client}")
    logging.info(f"Home: q.user is {q.user}")
    #logging.info(f"Home: q.app is {q.app}")

    #q.page['debug'] = cards.return_debug_card(q)
    #add_card(q, 'debug', await cards.return_debug_card(q, location='vertical'))

#    # this depends on student stage:
#
#    #cards.render_home_cards(q)
#
#    # By definition, students are registered so we at least know their name
#
#    if int(q.client.student_info['app_stage_id']) == 1:
#        card = cards.return_task1_card(location='top_horizontal', width='350px')
#        add_card(q, 'home/task1', card=card)
#
#        card = cards.return_demographics_card1(location='top_horizontal', width='400px')
#        add_card(q, 'home/demographics1', card)
#
#        card = cards.return_tasks_card(checked=0, location='top_horizontal', width='350px', height='400px')
#        add_card(q, 'home/tasks', card)
#
#    elif int(q.client.student_info['app_stage_id']) == 2:
#        card = cards.return_welcome_back_card(q, location='top_horizontal', height='400px', width='750px')
#        add_card(q, 'home/welcome_back', card=card)
#
#        card = cards.return_tasks_card(checked=1, location='top_horizontal', width='350px', height='400px')
#        add_card(q, 'home/tasks', card)
#
#    elif int(q.client.student_info['app_stage_id']) == 3:
#        card = cards.return_welcome_back_card(q, location='top_horizontal', height='400px', width='750px')
#        add_card(q, 'home/welcome_back', card=card)
#
#        card = cards.return_tasks_card(checked=2, location='top_horizontal', width='350px', height='400px')
#        add_card(q, 'home/tasks', card)
#
#    else:
#        card = cards.return_welcome_back_card(q, location='top_horizontal', height='400px', width='750px')
#        add_card(q, 'home/welcome_back', card=card)
#
#        card = cards.return_tasks_card(checked=4, location='top_horizontal', width='350px', height='400px')
#        add_card(q, 'home/tasks', card)

    await q.page.save()

#######################################################
####################  HOME EVENTS  ####################
#######################################################

async def next_demographic_1(q: Q) -> None:
    '''
    Respond to submission by clicking next on 'Tell us about yourself' card 1
    (from demographics1 function)
    '''
    # update existing card, do not recreate

    student_info = q.client.student_info
    student_info['financial_aid'] = q.args.financial_aid
    student_info['transfer_credits'] = q.args.transfer_credits
    logging.info(f'q.client.student_info: {q.client.student_info}')

    # need to add attendance to student_info
    q.client.my_dict = {
        'attendance': q.args.attendance
    }
    logging.info(f'q.client.my_dict: {q.client.my_dict}')

    resident_choices = [
        ui.choice('1', 'In-State'),
        ui.choice('2', 'Out-of-State'),
        ui.choice('3', 'Military'),
    ]
    logging.info('Updating home page')
    #q.page['meta'].redirect = '#home/1'
    q.page['demographics'].items = [
        ui.text_xl('Tell us more about yourself:'),
        ui.text('This information will help us estimate your tuition costs'),
        ui.choice_group(name='resident_status', label='My Resident status is', choices=resident_choices, required=True),
        ui.separator(label='', name='my_separator2', width='100%', visible=True),
        ui.button(name='next_demographic_2', label='Next', primary=True),
    ]

    await q.page.save()

async def next_demographic_2(q: Q) -> None:
    '''
    Respond to submission by clicking next on 'Tell us about yourself' card 1
    (from demographics1 function)
    '''
    # need to map these to the right place, this is a placeholder for now
    student_info = q.client.student_info
    if q.args.resident_status is not None:
        try:
            student_info['resident_status'] = int(q.args.resident_status)
        except ValueError:
            pass  # Handle the error or log it if needed
    logging.info(f'student_info: {student_info}')
    logging.info('Redirecting to the #program page')

    ## Instead of redirect, call the program function directly?
    #q.page['meta'].redirect = '#program'
    #q.page['sidebar'].value = '#program'
    await q.page.save()

#########################################################
####################  PROGRAMS PAGE  ####################
#########################################################

async def student_program(q: Q) -> None:
    '''
    Program page menu for students 
    (will also make a admin/coach version)
    '''
    clear_cards(q)
    location = 'top_vertical'
    student_info = q.client.student_info
    logging.info(f'Starting student_program')

    # I'm not sure why I need this
    if student_info['menu']['degree']:
        logging.info(f"student_info['menu']['degree']: {student_info['menu']['degree']}")
        #degree_id = int(student_info['menu']['degree'])

    add_card(q, 'explore_programs', ui.form_card(
        box=ui.box(location, width='100%'),
        items=[
            ui.text('**EXPLORE PROGRAMS** using the menus below. Click **Select > Save Program** to select your program.'),
            #ui.text('Explore Majors. Click **Select > Save Program** to select your program.'),
        ]
    ))
    await cards.render_dropdown_menus_horizontal(q, location=location, menu_width='300px')

    # Display program description, courses, and summary if program_id is defined
    if student_info['program_id']:
        logging.info(f"student_info['program_id']: {student_info['program_id']}")
        await cards.render_program_cards(q)

    await q.page.save()

#    if menu_degree == 1:
#        # Associate's Degree
#        clear_cards(['explore_programs', 'dropdown']) # clear all but the 
#        #await cards.render_program_description(q, location='top_vertical', height='250px', width='100%')
#        pass
#
#    elif menu_degree == 2: 
#        # Bachelor's Degree
#        clear_cards(['explore_programs', 'dropdown']) # clear all but the 
#        await cards.render_program_description(q, location='top_vertical', height='250px', width='100%')
#        await cards.render_program_table(q, location='horizontal', width='90%')
#        await cards.render_program_dashboard(q, location='horizontal', width='150px')
#
#    elif menu_degree == 5: 
#        # Undergraduate Certificate
#        pass
#
#    else:
#        # Graduate Certificate
#        pass

# defaults to student_program for now
async def admin_program(q: Q) -> None:
    await student_program(q)

async def program(q: Q):
    '''
    The main function for the Program page
    Called by @on('#program')
    '''
    clear_cards(q) # will use in the individual functions

    ### Could replace all of the below with student_program for now
    #if q.client.role:
    #    if q.client.role == 'admin':
    #        # admin program page
    #        await admin_program(q)
    #    elif q.client.role == 'coach':
    #        # coach program page
    #        await admin_program(q)
    #    else:
    #        # student program page
    #        await student_program(q)
    #else:
    #    # if role not defined
    #    # for now, default to student_program
    #    await student_program(q)

    await student_program(q)

    await q.page.save()

###############################################################
####################  PROGRAM MENU EVENTS  ####################
###############################################################

def reset_program(q: Q) -> None:
    '''
    When program is changed, multiple variables need to be reset
    '''
    q.client.student_info['menu']['program'] = None
    q.client.student_info['program_id'] = None
    q.client.student_info['degree_program'] = None

    q.client.student_data['required'] = None
    #q.client.student_data['periods'] = None
    q.client.student_data['schedule'] = None

    q.page['dropdown'].menu_program.value = None
    q.page['dropdown'].menu_program.choices = None

#######################################
## For "Degree" dropdown menu events ##
#######################################

async def menu_degree(q: Q):
    '''
    '''
    conn = q.client.conn
    student_info = q.client.student_info
    menu_degree_val = q.args.menu_degree
    logging.info('The value of menu_degree is ' + str(menu_degree_val))
    student_info['menu']['degree'] = menu_degree_val

    # reset area_of_study if degree changes
    student_info['menu']['area_of_study'] = None
    q.page['dropdown'].menu_area.value = None
    # update area_of_study choices based on degree chosen
    ## Note: without disabled this is disabling everything. This is a quick hack.
    q.page['dropdown'].menu_area.choices = \
        await get_choices(conn, area_query, params=(menu_degree_val,), disabled={""})

    # reset program if degree changes
    reset_program(q)

    #if student_info['menu']['degree'] == '2':
    #    # insert ge into student_info for bachelor's degree students if it does not already exist
    #    if not student_info['ge']:
    #        student_info['ge'] = initialize_ge()
    #else:
    #    #clear_cards(q, ['dropdown']) # clear everything except dropdown menus
    #    # remove ge from non-bachelor's degree students
    #    if student_info['ge']:
    #        del student_info['ge']

    #q.page['program.debug'].content = dropdown_debug(q)
    await q.page.save()

##############################################
## For "Area of Study" dropdown menu events ##
##############################################

async def menu_area(q: Q):
    '''
    '''
    disabled_programs = q.app.disabled_program_menu_items
    conn = q.client.conn
    student_info = q.client.student_info
    menu_area_val = q.args.menu_area
    logging.info('The value of area_of_study is ' + str(menu_area_val))
    student_info['menu']['area_of_study'] = menu_area_val

    # reset program if area_of_study changes
    reset_program(q)

    student_info['menu']['program'] = None
    q.page['dropdown'].menu_program.value = None

    # update program choices based on area_of_study chosen
    q.page['dropdown'].menu_program.choices = \
        await get_choices(conn, program_query, params=(student_info['menu']['degree'], menu_area_val),
            disabled=disabled_programs
        )

    # when new area of study is selected, remove description, courses, and summary
    # when new degree is selected, remove description, courses, and summary

#    clear_cards(q, ['dropdown'])
#    if q.client.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

#    q.page['debug_info'] = cards.return_debug_card(q, box='1 10 7 4') # update debug card
    await q.page.save()

########################################
## For "Program" dropdown menu events ##
########################################

async def menu_program(q: Q):
    conn = q.client.conn
    student_info = q.client.student_info
    menu_program_val = q.args.menu_program
    logging.info('The value of program is ' + str(menu_program_val))
    student_info['menu']['program'] = menu_program_val
    student_info['program_id'] = menu_program_val

    row = await get_program_title(conn, menu_program_val)
    if row:
        student_info['degree_program'] = row['title']
        student_info['degree_id'] = row['id']

    q.client.student_data['required'] = await get_required_program_courses(conn, menu_program_val)

    # need to also update q.client.student_info['degree_program']
    logging.info(f"This is menu_program(q): the value of program_id is {student_info['program_id']}")

    await cards.render_program_cards(q)
    
    # # program_id an alias used throughout


#    else:
#        clear_cards(q,['major_recommendations', 'dropdown'])
#        if hasattr(q.client, 'program_df'):
#            del q.client.program_df

    await q.page.save()



###########################################################
####################  PROGRAMS EVENTS  ####################
###########################################################

async def program_table(q: Q) -> None:
    '''
    Respond to events (clicking Course link or double-clicking row)
    in the table on Program page. This will display the course description
    by default.

    Notes:
      - q.args.table_name is set to [row_name]
      - the name of the table is 'program_table'
      - the name of the row is name = row['name']    
    '''
    coursename = q.args.program_table[0] 
    course_description_dialog(q, coursename, which='required')
    logging.info('The value of coursename in program_table is ' + coursename)
    await q.page.save()

async def view_program_description(q: Q) -> None:
    '''
    Respond to the menu event 'Course Description'
    (Calls same function as program_table above)
    '''
    coursename = q.args.view_program_description
    course_description_dialog(q, coursename, which='required')
    logging.info(f'The value of coursename in view_program_description is {coursename}')
    await q.page.save()

async def add_ge(q: Q):
    '''
    Respond to the menu event 'Add GE'
    (redirect to GE page)
    '''
    logging.info('Redirecting to the GE page')
    q.page['meta'].redirect = '#ge'
    await q.page.save()

async def add_elective(q: Q):
    '''
    Respond to the menu event 'Add Electives'
    '''
    logging.info(f'Redirecting to the Electives page')
    await q.page.save()

async def select_program(q: Q):
    '''
    Respond to the menu event 'Select Program'
    '''
    logging.info(f'Will select the program and save to student_info')
    await q.page.save()

########################################################
####################  COURSES PAGE  ####################
########################################################

###########################################################
####################  COURSES ACTIONS  ####################
###########################################################



#########################################################
####################  SCHEDULE PAGE  ####################
#########################################################

############################################################
####################  SCHEDULE ACTIONS  ####################
############################################################

#### OLD PAGES BELOW
#### USE AS EXAMPLES

async def page4(q: Q):
    q.page['sidebar'].value = '#page4'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # If first time on this page, create the card.
    add_card(q, 'form', ui.form_card(box='vertical', items=[
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1'),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox1', label='Textbox 1'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step2', label='Next', primary=True),
        ]),
    ]))

async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]

async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]
