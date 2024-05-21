
from utils import get_query, get_query_one, get_query_dict, get_query_df
from utils import get_choices, get_choices_with_disabled, get_role, get_program_title, \
    get_ge_choices, get_catalog_program_sequence, get_student_progress_d3
from utils import generate_periods, update_periods, generate_schedule, handle_prerequisites, \
    schedule_courses_old, update_courses, move_courses_forward


###########################################################

@on('#home')
async def home(q: Q):
    clear_cards(q)  # Drop all cards except main ones (header, sidebar, meta).

    ## get saved student information from the db and save to q.user.student_info variables
    ## (this is currently done at the initialize_user level)
    # - do this only at the first time, so we can navigate back to the home page and 
    #   not discard all the changes
    # - also, need to make this available for coaches by selecting that student
    #
    #if not q.user.student_info_populated:
    #    if q.user.role == 'student':
    #        await utils.populate_student_info(q, q.user.student_info['user_id'])
    #        q.user.student_info_populated = True

    # show this card only for guests and students with new status
    # for folks not yet logged in
#    if q.user.role == 'student' and q.user.student_info['app_stage_id'] > 1:
    if q.user.role == 'student':
        cards.render_welcome_card_old(q)
        cards.render_welcome_back_card(q, box='1 3 3 4')
    else:
        cards.render_welcome_card(q)
        cards.render_please_login(q)

#    student_profile_type = ['First time attending', 'Previous experience', 'Transfer credits']
#    add_card(q, 'student_profile_type_card', ui.form_card(
#        box=ui.box('middle_horizontal', width='250px'),
#        items=[
#            ui.choice_group(
#                name='student_profile_type',
#                label='Student Profile',
#                inline=False,
#                choices=[ui.choice(name=x, label=x) for x in student_profile_type],
#                value=q.client.student_profile_type if (q.client.student_profile_type is not None) else \
#                    q.args.student_profile_type,
#            )
#        ]
#    ))

    add_card(q, 'student_stub', cards.render_student_information_stub_card(box='4 3 4 2'))
    add_card(q, 'assessments', cards.render_career_assessment_card(box='4 5 4 2'))
    add_card(q, 'enable_ai', cards.render_ai_enablement_card(box='1 7 4 2'))
    add_card(q, 'major_recommendations', cards.render_major_recommendation_card(q, box='5 7 3 3'))

    #add_card(q, 'dashboard_placeholder', ui.markdown_card(
    #    box='6 6 2 2',
    #    title='Dashboard',
    #    content='Add a summary dashboard here'
    #))

    #add_card(q, 'to_do_next', ui.markdown_card(
    #    box='4 3 2 2',
    #    title='Next steps',
    #    content='Add links to continue, such as "Add Elective", "Update Schedule", etc.'
    #))
    if q.client.debug:
        add_card(q, 'debug_home', cards.render_debug_card(q, box='1 11 7 3')) 
    
## # ##############################################################
## # ###########  STUDENT PAGE                      ###############
## # ##############################################################

##############################################################
###########  PROGRAM PAGE (PREVIOUSLY MAJOR)   ###############
##############################################################
@on('#major')
async def major(q: Q):
    clear_cards(q)  

    add_card(q, 'dropdown',
        await cards.render_dropdown_menus_horizontal(q, 
            box='1 2 7 1', 
            menu_width='300px'
        )
    )
    # future: do this only for undergraduate degrees
    await cards.render_program(q)

    # if first time, add a blank card where table is 
    # and a blank card for credits
    #await render_program_dashboard(q, box='7 3 1 7')
    #await render_program_coursework_table(q, box='1 3 6 7')

#    #add_card(q, 'major1', ui.form_card(
#    #    box=ui.box('top_horizontal', width='250px'),
#    #    items=[
#    #        ui.text('Browse Majors', size=ui.TextSize.XL),
#    #        ui.text('State as **Browse Majors**'),
#    #        ui.text('Compare Majors', size=ui.TextSize.XL),
#    #        ui.text('Add **Compare Majors** functionality'),
#    #    ]
#    #))

    if q.client.debug:
        add_card(q, 'debug_program', cards.render_debug_card(q, box='1 11 7 3')) 

##############################################################
####################  COURSES PAGE  ##########################
##############################################################
@on('#course')
async def course(q: Q):
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    q.page['meta'].dialog = None # just in case, event closing not working currently

    # this is not working in guest mode now
    if q.user.student_info['menu']['program'] is not None:

        # check whether schedule was previously created
        if 'app_stage_id' in q.user.student_info:
            if q.user.student_info['app_stage_id'] is not None:
                stage_id=int(q.user.student_info['app_stage_id'])
                if stage_id==4:
                    ## retrieve schedule from database
                    q.user.student_info['df']['schedule'] = await get_student_progress_d3(q)

                    add_card(q, 'courses_instructions', ui.form_card(
                        box='1 2 7 1',
                        items=[
                            ui.text('**Instructions**: You have selected courses. You may now add electives or view your schedule.')
                        ]
                    ))
                    await cards.render_course_page_table(q, q.user.student_info['df']['schedule'], box='1 3 7 7')

                else: # stage_id==3:
                    cards.render_courses_header(q, box='1 2 7 1')
                    # need to build a program from scratch
                    # ask whether to start by pulling from catalog suggested programs


        #await cards.render_undergraduate_program(q)

    # starting to populate coursework... need to build this capability

    # check first that we are at the stage where this is available
    # instead of us having to build it. That stage is program_selected and catalog_selected. If
    # a schedule was ever created, we can retrieve it. 
    # if the_right_conditions_exist:
    
#    add_card(q, 'selected_program',
#        ui.form_card(
#        box='top_vertical',
#            items=[
#                ui.text(q.user.degree_program, size=ui.TextSize.XL) if q.user.degree_program else \
#                    ui.text('Degree program not yet selected.', size=ui.TextSize.L)
#            ]
#    ))
#
#    add_card(q, 'electives_tile', 
#        ui.wide_info_card(
#            box=ui.box('middle_horizontal', width='500px'),
#            name='', 
#            title='Explore Electives',
#            caption='Explore and perhaps recommend electives',
#    ))
#    add_card(q, 'minors_tile', 
#        ui.wide_info_card(
#            box=ui.box('middle_horizontal', width='500px'),
#            name='', 
#            title='Explore Minors',
#            caption='Explore and perhaps recommend minors',
#    ))
#   

    if q.client.debug:
        add_card(q, 'debug_course', cards.render_debug_card(q, box='1 11 7 3')) 

##############################################################
####################  GE PAGE (START) ########################
##############################################################
@on('#ge')
@on('goto_ge')
async def ge(q: Q):
    clear_cards(q)

    add_card(q, 'welcome_ge', ui.form_card(
        box='1 2 7 1',
        items=[
            ui.text_l('Select your General Education courses here.'),
            #ui.text('We will guide you through this experience.')
        ]
    ))
    menu_width = '300px'
    add_card(q, 'ge_req1', await cards.render_ge_comm_card(q, menu_width, box='1 3 3 4'))
    add_card(q, 'ge_req6', await cards.render_ge_research_card(q, menu_width, box='4 3 3 6'))
    add_card(q, 'ge_req4', await cards.render_ge_bio_card(q, menu_width, box='1 7 3 4'))
    add_card(q, 'ge_req2', await cards.render_ge_math_card(q, menu_width, box='4 9 3 2'))
    add_card(q, 'ge_req3', await cards.render_ge_arts_card(q, menu_width, box='1 11 3 3'))
    add_card(q, 'ge_req5', await cards.render_ge_beh_card(q, menu_width, box='4 11 3 3'))
 
#    
#    cards.render_debug(q)

###########################################################

@on('#electives')
async def electives(q: Q):
    clear_cards(q)
#    await ge(q)

###########################################################

@on('#schedule')
async def schedule(q: Q):
    clear_cards(q)
    q.page['meta'].dialog = None # just in case, event closing not working currently

    if q.user.student_info['first_term'] is None:
        q.user.student_info['first_term'] = 'spring2024' # need to set this default elsewhere
    await cards.render_schedule_menu(q)

    # this should be carried over from previous step, or any changes in course should be 
    # written to DB, our source of truth

    # this function pulls data from the db, we need to create it.
    # need to store for each student 
    # seq, name, course_type, 

    # get department recommended course list and schedule from catalog:
    #     student_progress_d3
    #
    
    # initialize student progress by picking undergraduate program from catalog
    query = '''
        INSERT INTO student_progress ( user_id, seq, course, course_type_id )
             SELECT ?, a.program_id, a.seq, a.course, a.course_type_id
             FROM catalog_program_sequence a
             WHERE program_id = ?
    '''
    # need to see if this works then wrap in error checking
    # 1 - if the result returns no rows (nothing is written)
    # 2 - if there is no corresponding user_id this will throw an error

    df = await utils.get_student_progress_d3(q)

    q.user.student_info['df']['schedule'] = df

    # Fix this to work with guest mode
    if q.user.student_info['df']['schedule'] is not None:
        degree_program = q.user.student_info['degree_program']
        add_card(q, 'schedule_instructions', ui.form_card(
            box='1 2 5 1',
            items=[
                ui.text(f'**{degree_program}**')
            ]
        ))
        await cards.render_schedule_page_table(q, df, box='1 7 7 6')

        ## display df
        start_term = 'Spring 2024' # pick this up from q.user variables
        # rename because the function uses 'period' rather than 'term'

        df_input = df.copy()
        df_input.rename(columns={'term': 'period'}, inplace=True)

        df_display, headers_display = utils.prepare_d3_data(df_input, start_term.upper())
        df_json = df_display.to_json(orient='records')
        headers_json = headers_display.to_json(orient='records')

        html_template = templates.html_code_minimal.format(
            javascript=templates.javascript_draw_only,
            headers=headers_json, 
            data=df_json)

        add_card(q, 'd3plot', cards.d3plot(html_template, box='1 3 5 4'))

        #######################################
        ## Scheduling and updating schedules ##
        #######################################

        # rescheduling given rules
        # pick these variables up from the form
        periods = utils.generate_periods(
            start_term='SPRING 2024', # pick up from q.user.X_ variable
            years=8, # number of years, more than we need
            max_courses=3, # pick up from courses_per_session
            sessions=[1, 3], # pick up from 'Sessions Attending'
            summer=True # attending summer? Add this to form!!
        )
        q.user.student_info['periods'] = periods # save to variable

        # updating syntax for fine-tuning max_courses, max_credits, etc. 
        updated_periods = utils.update_periods(periods, 
            "term == 'SUMMER' and year == 2024", 
            {"max_courses": 0}
        )
        q.user.student_info['periods'] = updated_periods # save to variable

#    #add_card(q, 'debug_schedule', cards.render_debug_user_card(q, box='1 9 7 2'))
    add_card(q, 'edit_sequence', ui.wide_info_card(
        box='', 
        name='', 
        title='Edit Sequence',
        caption='Add per-term control of course selection and sequence.'
    ))
#
#    add_card(q, 'lock_courses', ui.wide_info_card(
#        box=ui.box('grid', width='600px'), 
#        name='', 
#        title='Advice',
#        caption='Add hints and advice from counselors, e.g., "Not scheduling a class for session 2 will delay your graduation by x terms"'
#    ))

    if q.client.debug:
        add_card(q, 'debug_schedule', cards.render_debug_card(q, box='1 13 7 3')) 

## # #############################################################
## # ####################  PROJECT PAGE (START) ##################
## # #############################################################
## # 
## # @on('#project')
## # async def project(q: Q):
## #     clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
## # 
## #     card = await cards.render_project_table(templates.project_data, box='1 2 7 9', height='700px')
## #     add_card(q, 'project_table_location', card)
## # 
## # ################################################################################
## # 
## # warning_example_card = ui.form_card(
## #     box='1 1 4 7',
## #     items=[
## #         ui.message_bar(type='blocked', text='This action is blocked.'),
## #         ui.message_bar(type='error', text='This is an error message'),
## #         ui.message_bar(type='warning', text='This is a warning message.'),
## #         ui.message_bar(type='info', text='This is an information message.'),
## #         ui.message_bar(type='success', text='This is an success message.'),
## #         ui.message_bar(type='danger', text='This is a danger message.'),
## #         ui.message_bar(type='success', text='This is a **MARKDOWN** _message_.'),
## #         ui.message_bar(type='success', text='This is an <b>HTML</b> <i>message</i>.'),
## #     ]
## # )

###########################################
### For "Recommend a major" card events ###
###########################################

@on()
async def show_recommendations(q: Q):
    option = q.args.recommendation_group
    message = 'The value of show_recommendations is ' + str(option)
    logging.info(message)
#    q.page['info'] = ui.form_card(box='2 4 4 2', items=[
#        ui.message_bar(type='info', text=message)
#        ]) 
    await utils.recommend_a_major(q, option)

@on()
async def clear_recommendations(q: Q):
    q.args.recommendation_group = None

################################################################################

@on()
async def user_role(q: Q):
    logging.info('The value of user_role is ' + str(q.args.user_role))
    q.user.user_role = q.args.user_role
#    #if q.user.degree != '2':
#    #    clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#    #    del q.client.program_df
    await q.page.save()

#######################################################
### Program page: For "Degree" dropdown menu events ###
#######################################################

@on()
async def menu_degree(q: Q):
    logging.info('The value of menu_degree is ' + str(q.args.menu_degree))
    timedConnection = q.user.conn
    q.user.student_info['menu']['degree'] = q.args.menu_degree

    # reset area_of_study if degree changes
    q.user.student_info['menu']['area_of_study'] = None
    q.page['dropdown'].menu_area.value = None
    # update area_of_study choices based on degree chosen
    q.page['dropdown'].menu_area.choices = await get_choices(timedConnection, cards.area_query, 
        params=(q.user.student_info['menu']['degree'],))

    # reset program if degree changes
    utils.reset_program(q)

    if q.user.student_info['menu']['degree'] == '2':
        # insert ge into student_info for bachelor's degree students
        q.user.student_info['ge'] = utils.initialize_ge()
        pass
    else:
        clear_cards(q, ['dropdown']) # clear everything except dropdown menus
        # remove ge from non-bachelor's degree students
        if 'ge' in q.user.student_info:
            del q.user.student_info['ge']

##    if q.client.major_debug:
    q.page['debug_info'] = cards.render_debug_card(q, box='1 10 7 4') # update debug card
#
##        q.page['debug_client_info'] = cards.render_debug_client_card(q)
##        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    await q.page.save()

##############################################################
### Program page: For "Area of Study" dropdown menu events ###
##############################################################

@on()
async def menu_area(q: Q):
    logging.info('The value of area_of_study is ' + str(q.args.menu_area))
    timedConnection = q.user.conn
    q.user.student_info['menu']['area_of_study'] = q.args.menu_area

    # reset program if area_of_study changes
    utils.reset_program(q)

    #q.user.student_info['menu']['program'] = None
    #q.page['dropdown'].menu_program.value = None

    # update program choices based on area_of_study chosen
    q.page['dropdown'].menu_program.choices = await get_choices(timedConnection, cards.program_query, 
        params=(q.user.student_info['menu']['degree'], q.user.student_info['menu']['area_of_study']))

#    if q.user.degree != '2':
#        clear_cards(q,['major_recommendations', 'dropdown']) # clear possible BA/BS cards
#        del q.client.program_df

    q.page['debug_info'] = cards.render_debug_card(q, box='1 10 7 4') # update debug card
    await q.page.save()

########################################################
### Program page: For "Program" dropdown menu events ###
########################################################

@on()
async def menu_program(q: Q):
    logging.info('The value of program is ' + str(q.args.menu_program))
    timedConnection = q.user.conn
    q.user.student_info['menu']['program'] = q.args.menu_program
    q.user.student_info['program_id'] = q.user.student_info['menu']['program'] # program_id an alias used throughout
    result = await get_program_title(timedConnection, q.user.student_info['program_id'])
    q.user.student_info['degree_program'] = result['title']
    
    # have the size of this depend on the degree (?)
    if q.user.student_info['menu']['degree'] == '2':
        await cards.render_program(q)
    #else:
        # Insert a blank card with a message - "has to be completed"

        ##await cards.render_program_description(q, box='1 3 7 2')
        ##await cards.render_program_dashboard(q, box='7 5 1 5') # need to fix
        ##await cards.render_program_coursework_table(q, box='1 5 6 5')

#    else:
#        clear_cards(q,['major_recommendations', 'dropdown'])
#        if hasattr(q.client, 'program_df'):
#            del q.client.program_df

#    if q.client.major_debug:
#        q.page['debug_info'] = cards.render_debug_card(q) # update debug card
#        q.page['debug_client_info'] = cards.render_debug_client_card(q)
#        q.page['debug_user_info'] = cards.render_debug_user_card(q)
    q.page['debug_info'] = cards.render_debug_card(q, box='1 10 7 4') # update debug card
    await q.page.save()

################################################################################

##################################################################################
### Program page: Create Description popup for table by clicking on table row  ###
### on course name link or double-clicking course row                          ###
##################################################################################

@on()
async def program_table(q: Q):
    # note: q.args.table_name is set to [row_name]
    # the name of the table is 'program_table'
    # the name of the row is name=row['course'], the course name
    coursename = q.args.program_table[0] # am I getting coursename wrong here?
    #cards.render_dialog_description(q, coursename)
    cards.render_description_dialog(q, coursename)
    logging.info('The value of coursename in program_table is ' + coursename)

    await q.page.save()

################################################################################

@on()
async def view_description(q: Q):
    # Note: same function as program_table(q) called by view_description menu option
    coursename = q.args.view_description
#    cards.render_dialog_description(q, coursename)
    cards.render_description_dialog(q, coursename)

    logging.info('The value of coursename in view_description is ' + str(coursename))

    await q.page.save()

################################################################################

@on('render_dialog_description.dismissed')
async def render_dialog_description_dismissed(q: Q):
    """
    Dismiss dialog.
    """
    logging.info('Dismissing dialog')
    q.page['meta'].dialog = None

    await q.page.save()

@on('render_description_dialog.dismissed')
async def render_description_dialog_dismissed(q: Q):
    """
    Dismiss dialog.
    """
    logging.info('Dismissing dialog')
    q.page['meta'].dialog = None

    await q.page.save()

################################################################################

@on()
async def student_dropdown(q: Q):
    logging.info('The value of user_dropdown is ' + str(q.args.user_dropdown))
    q.user.user_dropdown = q.args.user_dropdown

################################################################################


###############################################
### Schedule page: For schedule_menu events ###
###############################################
@on()
async def submit_schedule_menu(q: Q):
    '''
    Click 'Submit' on options on Schedule page for card 'schedule_menu'
    '''
    logging.info('Submit option on schedule page')
    # to do: finish code here

    await schedule(q) # dummy, just reload schedule page. remove when function is completed
    await q.page.save()
    
@on()

async def reset_schedule_menu(q: Q):
    '''
    Click 'Reset' on options on Schedule page for card 'schedule_menu'

    Need to store original options in a dictionary that can be reapplied here 
    if someone clicks Reset. Either that, or I should rerun the function from 
    the beginning with its defaults.
    '''
    logging.info('Reset option on schedule page')
    # to do: finish code here

    await schedule(q) # dummy, just reload schedule page. remove when function is completed
    await q.page.save()


################################################################################

###############################################################################
####################  Initialize app, user, client Functions ##################
###############################################################################
    

async def initialize_client(q: Q):
    """
    Initialize the client (once per connection)
    """
    logging.info('Initializing client')
    q.client.initialized = True
    q.client.cards = set()
    q.page['meta'] = cards.render_meta_card()
    q.page['header'] = cards.render_header(q)
    q.page['footer'] = cards.render_footer()

    # Debug status
    q.client.debug = True

    if q.args['#'] is None:
        await home(q)


## Below needs some editing, from ChatGPT

from h2o_wave import main, app, Q, ui
from requests_oauthlib import OAuth2Session

client_id = 'myapp'
client_secret = 'YOUR_CLIENT_SECRET'
authorization_base_url = 'http://localhost:8080/realms/myrealm/protocol/openid-connect/auth'
token_url = 'http://localhost:8080/realms/myrealm/protocol/openid-connect/token'
redirect_uri = 'http://localhost:10101/_auth_callback'

oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

@app('/login')
async def serve(q: Q):
    if q.args.oauth_callback:
        token = oauth.fetch_token(token_url, client_secret=client_secret,
                                  authorization_response=q.args.oauth_callback)
        q.user.token = token
        user_info = oauth.get('http://localhost:8080/realms/myrealm/protocol/openid-connect/userinfo').json()
        q.user.username = user_info['preferred_username']
        q.user.roles = user_info['roles']  # Assumes roles are included in user info
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text(f'Welcome, {q.user.username}!'),
            ui.button(name='logout', label='Logout', primary=True)
        ])
    elif q.args.logout:
        q.user.token = None
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text('You have been logged out.'),
            ui.button(name='login_oauth', label='Login with OAuth', primary=True)
        ])
    elif q.args.login_oauth:
        authorization_url, state = oauth.authorization_url(authorization_base_url)
        q.page['form'] = ui.redirect(authorization_url)
    else:
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.button(name='login_oauth', label='Login with OAuth', primary=True)
        ])
    await q.page.save()

@app('/home')
async def home(q: Q):
    if 'student' in q.user.roles:
        await show_student_home(q)
    elif 'coach' in q.user.roles:
        await show_coach_home(q)
    elif 'admin' in q.user.roles:
        await show_admin_home(q)
    else:
        await show_access_denied(q)

async def show_student_home(q: Q):
    q.page['form'] = ui.form_card(box='1 1 2 2', items=[
        ui.text(f'Welcome to the student home page, {q.user.username}!'),
        ui.link(label='Tasks', path='/student/tasks'),
        ui.link(label='Courses', path='/student/courses')
    ])
    await q.page.save()

async def show_coach_home(q: Q):
    q.page['form'] = ui.form_card(box='1 1 2 2', items=[
        ui.text(f'Welcome to the coach home page, {q.user.username}!'),
        ui.link(label='Student Home', path='/student/home'),
        ui.link(label='Tasks', path='/coach/tasks')
    ])
    await q.page.save()

async def show_admin_home(q: Q):
    q.page['form'] = ui.form_card(box='1 1 2 2', items=[
        ui.text(f'Welcome to the admin home page, {q.user.username}!'),
        ui.link(label='Student Home', path='/student/home'),
        ui.link(label='Coach Tasks', path='/coach/tasks'),
        ui.link(label='Admin Tasks', path='/admin/tasks'),
        ui.link(label='Admin Page', path='/admin/admin')
    ])
    await q.page.save()

async def show_access_denied(q: Q):
    q.page['form'] = ui.form_card(box='1 1 2 2', items=[
        ui.text('Access Denied.'),
        ui.button(name='logout', label='Logout', primary=True)
    ])
    await q.page.save()

@app('/student/tasks')
async def student_tasks(q: Q):
    if 'student' in q.user.roles or 'coach' in q.user.roles or 'admin' in q.user.roles:
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text(f'{q.user.username}, here are your tasks.')
        ])
    else:
        await show_access_denied(q)
    await q.page.save()

@app('/student/courses')
async def student_courses(q: Q):
    if 'student' in q.user.roles or 'coach' in q.user.roles or 'admin' in q.user.roles:
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text(f'{q.user.username}, here are your courses.')
        ])
    else:
        await show_access_denied(q)
    await q.page.save()

@app('/coach/tasks')
async def coach_tasks(q: Q):
    if 'coach' in q.user.roles or 'admin' in q.user.roles:
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text(f'{q.user.username}, here are your coach tasks.')
        ])
    else:
        await show_access_denied(q)
    await q.page.save()

@app('/admin/tasks')
async def admin_tasks(q: Q):
    if 'admin' in q.user.roles:
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text(f'{q.user.username}, here are your admin tasks.')
        ])
    else:
        await show_access_denied(q)
    await q.page.save()

@app('/admin/admin')
async def admin_admin(q: Q):
    if 'admin' in q.user.roles:
        q.page['form'] = ui.form_card(box='1 1 2 2', items=[
            ui.text(f'{q.user.username}, welcome to the admin page.')
        ])
    else:
        await show_access_denied(q)
    await q.page.save()