
######################################################
####################  Login page  ####################
######################################################

@on('#login')
async def login(q: Q):
    clear_cards(q)
    card_height = '400px'

    #q.page['header'] = cards.return_login_header_card(q)
    #cards.render_welcome_back_card(q, width='400px', height=card_height, location='top_vertical')

    #cards.render_login_welcome_card(q, cardname='welcome_login', location='top_horizontal')
    card = cards.return_login_welcome_card(q, location='top_horizontal', width='100%')
    add_card(q, 'login/welcome', card)

    card = await cards.return_user_login_dropdown(q, location='horizontal', menu_width='300px')
    add_card(q, 'login/demo_login', card)

    if q.app.debug:
        q.page['debug'] = await cards.return_debug_card(q)

    await q.page.save()

# respond to sample user selection
@on()
async def select_sample_user(q: Q):
    '''
    Respond to sample user selection from cards.render_user_dropdown
    '''
    choice = q.args.choice_group
    logging.info('The selected user is: ' + choice)
    q.user.user_id = int(choice)
    
    # initialize all student_info stuff
    await utils.reset_student_info_data(q)
    q.user.student_info_populated = False

    # Guest has user_id = 0
    if q.user.user_id > 0:
        q.user.logged_in = True
        # get role for logged in user
        await utils.set_user_vars_given_role(q) # assigns q.user.role_id, q.user.username, q.user.name

        # Admin path:
        #   - Can add users
        #   - Can set or change user roles
        #   - Can do other administrative tasks
        #   - Can do everything a coach can do
        #
        # Coach path:
        #   - Can add students
        #   - Using pulldown menu to select student,
        #     can profile, select program, select courses, schedule courses for students
        #
        # Student path:
        #   - Can profile, select program, select courses, schedule courses for themselves
        #
        # Guest path:
        #   - Can do everything a student can do except save their info to the database 
        #
        if q.user.role in ['coach', 'admin']:
            pass
        elif q.user.role == 'student':
            await utils.populate_student_info(q, q.user.user_id)
            #await utils.populate_q_student_info(q, q.user.conn, q.user.user_id)
            q.user.student_info_populated = True

    else:
        #await utils.reset_student_info_data(q) # already done?
        pass

    # update header 
    q.page['header'] = cards.return_header_card(q)

    # update debug card
    if q.app.debug:
        q.page['debug'].content = f'''
### q.args values:
{q.args}

### q.events values:
{q.events}

### q.client value:
{q.client}

### q.user.student_info values:
{q.user.student_info}

### q.user values:
{q.user}
        '''

    # redirect to #home route
    q.page['meta'].redirect = '#home'    
        
    await q.page.save()



async def admin_skills(q: Q) -> None:
    await student_skills(q)

async def coach_skills(q: Q) -> None:
    await student_skills(q)

async def student_skills(q: Q) -> None:
    clear_cards(q)
    timed_connection = q.user.conn
    card = await return_skills_menu(timed_connection, location='vertical', width='300px')
    add_card(q, 'skill_card', card)
    await q.page.save()

    #if q.user.student_info['menu']['degree']:
    #    degree_id = int(q.user.student_info['menu']['degree'])

    #add_card(q, 'explore_programs', ui.form_card(
    #    box=ui.box('top_vertical', width='100%'),
    #    items=[
    #        ui.text('**EXPLORE PROGRAMS** using the menus below. Click **Select > Save Program** to select your program.'),
    #        #ui.text('Explore Majors. Click **Select > Save Program** to select your program.'),
    #    ]
    #))    
    #await frontend.render_dropdown_menus_horizontal(q, location='top_vertical', menu_width='300px')


    ## render program after getting the list of programs
    #if q.user.student_info['program_id']:
    #    await cards.render_program(q)

@on('#skills')
async def skills(q: Q):
    clear_cards(q) # will use in the individual functions

    timed_connection = q.user.conn
    card = await return_skills_menu(timed_connection, location='vertical', width='300px')
    add_card(q, 'skill_card', card)
#    await q.page.save()


#    if q.user.role == 'admin':
#        # admin program page
#        await admin_skills(q)
#
#    elif q.user.role == 'coach':
#        # coach program page
#        await coach_skills(q)
#        
#    elif q.user.role == 'student':
#        # student program page
#        await student_skills(q)
#        
#    else:
#        # need to raise an error here
#        pass
#    
#    if q.app.debug_program:
#        add_card(q, 'skills_debug', await cards.return_debug_card(q))

    await q.page.save()
