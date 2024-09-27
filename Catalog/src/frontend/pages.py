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

    #logging.info(f"Home: q.client is {q.client}")
    #logging.info(f"Home: q.user is {q.user}")
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
    q.page['sidebar'].value = '#program'


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
    q.page['sidebar'].value = '#ge'

    await q.page.save()

async def add_elective(q: Q):
    '''
    Respond to the menu event 'Add Electives'
    '''
    logging.info(f'Redirecting to the Electives page')
    q.page['meta'].redirect = '#electives'
    q.page['sidebar'].value = '#electives'

    await q.page.save()

async def select_program(q: Q):
    '''
    Respond to the menu event 'Select Program'
    '''
    logging.info(f'Will select the program and save to student_info')
    await q.page.save()

#######################################################
####################  SKILLS PAGE  ####################
#######################################################

async def skills(q: Q):
    clear_cards(q) # will use in the individual functions

    conn = q.client.conn
    add_card(q, 'welcome_skills', ui.form_card(
        box=ui.box('top_horizontal', width='100%'),
        items=[
            ui.text_xl('Select two or more skills to find matching programs'),
            #ui.text('We will guide you through this experience.')
            #ui.inline([
            #    ui.text('Click here to display courses without prerequisites:', size=ui.TextSize.L),
            #    ui.checkbox(name='ge_all_nopre', label='')
            #], align='start'),
        ]
    ))
    card = await cards.return_skills_menu_card(conn, location='top_vertical', width='300px')
    add_card(q, 'skill_card', card)
    await q.page.save()

##########################################################
####################  SKILLS ACTIONS  ####################
##########################################################

async def submit_skills_menu(q: Q):
    """
    Respond to Submit button on Skills menu
    """
    conn = q.client.conn
    selected_skills = q.args.skills_checklist
    q.client.skills = {}
    q.client.skills['selected'] = selected_skills

    result_limit = 15
    #result_limit = int(q.args.result_limit)

    if not selected_skills:
        # throw an error, not sure that this works
        q.page['skills_results'] = ui.form_card(box='debug', items=[ui.message_bar('No skills selected', type='warning')])
        return

    if len(selected_skills) == 1:
        q.page['skills_results'] = ui.form_card(box='debug', items=[
            ui.message_bar('Please select more than one skill', type='error')
        ])
        return
    
    # Convert selected skills to a tuple for SQL query
    skills_tuple = tuple(selected_skills)
    int_tuple = tuple(map(int, skills_tuple))

    query = f"""
        SELECT b.id, a.program, sum(a.score) AS TotalScore 
        FROM program_skill_score_view a, programs b

        WHERE a.skill_id IN {int_tuple}
            AND b.degree_id = 3
            AND a.program = b.name 
        GROUP BY a.program
        ORDER BY TotalScore DESC 
        LIMIT {result_limit}
    """
    results = await conn.query_dict(query)

    # save for reuse
    q.client.student_data['skills'] = results
    card = await cards.return_skills_table(results)
    add_card(q, 'skills_program_table', card)

async def program_skills_table(q: Q):
    '''
    Respond to events (clicking table link or double-clicking row)
    in the table on Program page. This will display the course description
    by default.

    Notes:
      - q.args.table_name is set to [row_name]
      - the name of the table is 'program_table'
      - the name of the row is name = row['name']    
    '''
    program_val = int(q.args.program_skills_table[0])
    conn = q.client.conn
    logging.info(f'The value of program is {program_val}')
    student_info = q.client.student_info
    student_info['program_id'] = int(program_val)

    row = await get_program_title(conn, program_val)
    if row:
        student_info['degree_program'] = row['title']
        student_info['degree_id'] = row['id']

    logging.info(f"The value of title is {student_info['degree_program']}")
    logging.info(f"The value of degree_id is {student_info['degree_id']}")

    q.client.student_data['required'] = await get_required_program_courses(conn, student_info['program_id'])

    # need to also update q.client.student_info['degree_program']
    #logging.info(f"This is menu_program(q): the value of program_id is {student_info['program_val']}")

    #await cards.render_program_cards(q)
    clear_cards(q, [])
    await cards.render_program_description_card(q, location='top_vertical', height='200px', width='100%')
    await cards.render_program_table(q, location='horizontal', width='90%')
    await cards.render_program_dashboard_card(q, location='horizontal', width='150px')

    
    # # program_id an alias used throughout

    await q.page.save()


##############

    ##frontend.course_description_dialog(q, coursename, which='required')
    #clear_cards(q)
    ##q.client.student_info[] = program_name
    #await cards.render_program_cards(q)
    #logging.info(f'The value of program_name in program_skills_table is {program_name}')
    #await q.page.save()

async def explore_skills_program(q: Q):
    '''
    Respond to the menu event 'Explore Program'
    [Should be similar to what is found in #programs ]
    '''
    which_program = q.args.explore_skills_program
    #frontend.course_description_dialog(q, coursename, which='required')
    logging.info('The value of which_program in explore_skills_program is ' + str(which_program))
    await q.page.save()

async def select_skills_program(q: Q):
    '''
    Respond to the menu event 'Select Program'
    [Should be identical to what is found in #programs under Select]
    '''
    which_program = q.args.select_skills_program
    #frontend.course_description_dialog(q, coursename, which='required')
    logging.info(f'The value of which_program in select_skills_program is {which_program}')
    await q.page.save()

########################################################
####################  COURSES PAGE  ####################
########################################################

async def student_course(q: Q):
    if q.client.student_data['schedule'] is not None:
        add_card(q, 'courses_instructions', ui.form_card(
            box='top_horizontal',
            items=[
                ui.text('**Instructions**: You have selected courses. You may now add electives or view your schedule.')
            ]
        ))
        await cards.render_course_page_table_use(q, location='vertical')

    await q.page.save()

async def admin_course(q: Q):
    await student_course(q)

async def coach_course(q: Q):
    await student_course(q)

async def courses(q: Q):
    clear_cards(q)

    if q.client.role == 'admin':
        # admin course page
        await admin_course(q)

    elif q.client.role == 'coach':
        # coach course page
        await coach_course(q)
        
    elif q.client.role == 'student':
        # student course page
        await student_course(q)
        
    else:
        await student_course(q)
        
    await q.page.save()

###########################################################
####################  COURSE ACTIONS  ####################
###########################################################

###################################################
####################  GE PAGE  ####################
###################################################

async def student_ge(q: Q):
    clear_cards(q)

    add_card(q, 'welcome_ge', ui.form_card(
        box=ui.box('horizontal', width='100%'),
        items=[
            ui.text_xl('Select your General Education courses here.'),
            #ui.text('We will guide you through this experience.')
            ui.inline([
                ui.text('Click to display courses without prerequisites:', size=ui.TextSize.L),
                ui.checkbox(name='ge_all_nopre', label='')
            ], align='start'),
        ]
    ))
    menu_width = '300px'
    location = 'grid'
    width = '330px'
    await cards.render_ge_comm_card(q, cardname='ge_comm', location=location, width=width)
    await cards.render_ge_res_card(q, cardname='ge_res', location=location, width=width)
    await cards.render_ge_bio_card(q, cardname='ge_bio', location=location, width=width)
    await cards.render_ge_math_card(q, cardname='ge_math', location=location, width=width)
    await cards.render_ge_arts_card(q, cardname='ge_arts', location=location, width=width)
    await cards.render_ge_beh_card(q, cardname='ge_beh', location=location, width=width)

async def admin_ge(q: Q):
    await student_ge(q)

async def ge(q: Q):
    clear_cards(q)

    if q.client.role == 'admin':
        # admin ge page
        await admin_ge(q)

    elif q.client.role == 'coach':
        # coach ge page
        await admin_ge(q)
        
    elif q.client.role == 'student':
        # student ge page
        await student_ge(q)
        
    else:
        await student_ge(q)
        
    #if q.app.debug:
    #    add_card(q, 'ge_debug', await cards.return_debug_card(q))

    await q.page.save()

######################################################
####################  GE ACTIONS  ####################
######################################################

#############
## GE Arts ##  
#############

async def ge_arts_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['arts']['nopre'] = True
    await q.page.save()

async def ge_arts_1(q: Q):
    q.client.student_info['ge']['arts']['1'] = q.args.ge_arts_1
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_arts_2(q: Q):
    q.client.student_info['ge']['arts']['2'] = q.args.ge_arts_2
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Beh ##
############

async def ge_beh_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['beh']['nopre'] = True
    await q.page.save()

async def ge_beh_1(q: Q):
    q.client.student_info['ge']['beh']['1'] = q.args.ge_beh_1
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_beh_2(q: Q):
    q.client.student_info['ge']['beh']['2'] = q.args.ge_beh_2
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Bio ##
############

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

async def ge_bio_2(q: Q):
    q.client.student_info['ge']['bio']['2'] = q.args.ge_bio_2
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#############
## GE Comm ##  These all work !!!
#############

async def ge_comm_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['comm']['nopre'] = True
    await q.page.save()

async def ge_comm_1(q: Q):
    q.client.student_info['ge']['comm']['1'] = q.args.ge_comm_1
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_comm_2(q: Q):
    q.client.student_info['ge']['comm']['2'] = q.args.ge_comm_2
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_comm_3(q: Q):
    q.client.student_info['ge']['comm']['3'] = q.args.ge_comm_3
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_comm_4(q: Q):
    q.client.student_info['ge']['comm']['4'] = q.args.ge_comm_4
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#############
## GE Math ##  This works! 
#############

async def ge_math_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['math']['nopre'] = True
    await q.page.save()

async def ge_math_1(q: Q):
    q.client.student_info['ge']['math']['1'] = q.args.ge_math_1
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

############
## GE Res ##
############

async def ge_res_check(q: Q):
    # set nopre = True
    q.client.student_info['ge']['res']['nopre'] = True
    await q.page.save()

async def ge_res_1(q: Q):
    q.client.student_info['ge']['res']['1'] = q.args.ge_res_1
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_res_2(q: Q):
    q.client.student_info['ge']['res']['2'] = q.args.ge_res_2
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_res_3(q: Q):
    q.client.student_info['ge']['res']['3'] = q.args.ge_res_3
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_res_3a(q: Q):
    q.client.student_info['ge']['res']['3a'] = q.args.ge_res_3a
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_res_3b(q: Q):
    q.client.student_info['ge']['res']['3b'] = q.args.ge_res_3b
    # reset dropdown menu items?
    #q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

async def ge_res_3c(q: Q):
    q.client.student_info['ge']['res']['3c'] = q.args.ge_res_3c
    pass
    # reset dropdown menu items?
    # q.page['ge_debug'].content = ge_debug_content(q)
    await q.page.save()

#########################################################
####################  SCHEDULE PAGE  ####################
#########################################################

async def student_schedule(q: Q):
    student_data = q.client.student_data
    student_info = q.client.student_info

    if student_data['schedule'] is not None:
        # need to check whether all terms and sessions are all 0,
        # meaning a schedule template was created but no classes
        # were actually scheduled

        html_template = cards.create_html_template(
            df = student_data['schedule'], 
            start_term = student_info['first_term']
        )

        await cards.render_d3plot(q, html_template, location='horizontal', width='75%', height='400px')
        await cards.render_schedule_menu(q, location='horizontal', width='20%')
        await cards.render_schedule_page_table(q, location='vertical', width='100%')

async def admin_schedule(q: Q):
    await student_schedule(q)

async def schedule(q: Q):
    clear_cards(q)
    q.page['sidebar'].value = '#schedule'

    student_info = q.client.student_info
    # first term is required for all scheduling
    # this should create the default for the pulldown 'First Term' menu
    if student_info['first_term'] is None:
        student_info['first_term'] = q.app.default_first_term

    if q.client.role == 'admin':
        # admin schedule page
        await admin_schedule(q)

    elif q.client.role == 'coach':
        # coach schedule page
        await admin_schedule(q)
        
    elif q.client.role == 'student':
        # student schedule page
        await student_schedule(q)
        
    else:
        await student_schedule(q)
        #pass
        
    await q.page.save()

############################################################
####################  SCHEDULE ACTIONS  ####################
############################################################

###########################
## Schedule Menu actions ##
###########################

async def submit_schedule_menu(q: Q):
    '''
    Respond to Submit button on menu on Schedule page
    Launch generate_periods(start_term='SPRING 2024', years=8, max_courses=3, max_credits=18, 
                     summer=False, sessions=[1,3], as_df=True):
    '''
    schedule_menu = {}
    schedule_menu['first_term'] = q.args.first_term
    schedule_menu['sessions'] = q.args.sessions_checklist
    schedule_menu['max_courses'] = q.args.courses_per_session
    schedule_menu['max_credits'] = q.args.max_credits
    schedule_menu['attend_summer'] = q.args.attend_summer
    q.client.student_info['schedule_menu'] = schedule_menu

    q.client.student_data['periods'] = utils.generate_periods(
            start_term=schedule_menu['first_term'],
            max_courses=schedule_menu['max_courses'],
            max_credits=schedule_menu['max_credits'],
            summer=schedule_menu['attend_summer'],
            sessions=schedule_menu['sessions'],
            as_df=True
        )

    q.page['schedule_debug'].content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.client.student_info values:
{q.client.student_info}

### q.client.student_info['schedule_menu'] values:
{q.client.student_info['schedule_menu']}

### q.client.student_data values:

#### Required:
{q.client.student_data['required']}

#### Periods:
{q.client.student_data['periods']}

#### Schedule:
{q.client.student_data['schedule']}
    '''
    await q.page.save()


############################
## Schedule Table actions ##
############################

async def schedule_table(q: Q):
    '''
    Respond to events (clicking Course link or double-clicking row)
    in the table on Schedule page. This will display the course description
    by default.

    Notes:
      - q.args.table_name is set to [row_name]
      - the name of the table is 'schedule_table'
      - the name of the row is name = row['name']    
    '''
    coursename = q.args.schedule_table[0] # am I getting coursename wrong here?
    frontend.course_description_dialog(q, coursename, which='schedule')
    logging.info('The value of coursename in schedule_table is ' + coursename)
    await q.page.save()

# view description
async def view_schedule_description(q: Q):
    '''
    Respond to the menu event 'Course Description'
    (Calls same function as schedule_table above)
    '''
    coursename = q.args.view_schedule_description
    frontend.course_description_dialog(q, coursename, which='schedule')
    logging.info('The value of coursename in view_schedule_description is ' + str(coursename))
    await q.page.save()

# move class
async def move_class(q: Q):
    pass

# lock class
async def lock_class(q: Q):
    pass

# select elective (may be multiple tables)
async def select_elective(q: Q):
    pass
