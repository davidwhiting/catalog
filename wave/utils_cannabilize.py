
######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

#############################################################
####################  Initialize Functions ##################
#############################################################

## Note: moved initialize_app, initialize_user, initialize_client functions
## to app.py to avoid circular import references between utils.py and cards.py

######################################################################



######################################################################
#####################  QUERIES & FUNCTIONS  ##########################
######################################################################

async def get_ge_choices(conn, query, params=()):
    rows = await get_query(conn, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['name'] + ': ' + row['title']) for row in rows]
    return choices

async def get_catalog_program_sequence(q):
    query = 'SELECT * FROM catalog_program_sequence_view WHERE program_id = ?'
    df = await get_query_df(q.user.conn, query, params=(q.user.student_info['program_id'],))
    return df



async def get_choices_with_disabled_old(timedConnection, query, params=()):
    '''
    Note: consolidate with get_choices to add a disabled={} option
    '''
    disabled_items = {
        'Cybersecurity Technology',
        'Social Science',
        'Applied Technology',
        'Web and Digital Design',        
        'East Asian Studies',
        'English',
        'General Studies',
        'History'
    }
    rows = await get_query(timedConnection, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label'], \
        disabled=(str(row['label']) in disabled_items)) for row in rows]
    return choices

async def get_choices_with_disabled(timedConnection, query, params=()):
    '''
    Note: consolidate with get_choices to add a disabled={} option
    '''
    disabled_items = {
        'Cybersecurity Technology',
        'Social Science',
        'Applied Technology',
        'Web and Digital Design',        
        'East Asian Studies',
        'English',
        'General Studies',
        'History'
    }
    rows = await get_query(timedConnection, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label'], \
        disabled=(str(row['label']) in disabled_items)) for row in rows]
    return choices

######################################################################
#################  EVENT AND HANDLER FUNCTIONS  ######################
######################################################################

async def recommend_a_major(q, choice):
    '''
    Placeholder for the render_major_recommendation_card event
    '''
    def _to_be_implemented(q, label, box='3 6 5 1', type='info'):
        message = label + ' has not been implemented yet'
        q.page['info'] = ui.form_card(box=box, items=[
            ui.message_bar(type='warning', text=message)
        ]) 
    if choice == 'A':
        label = 'Recommendation engine for "My interests"'
    elif choice == 'B':
        label = 'Recommendation engine for "My skills"'
    elif choice == 'C':
        label = 'Recommendation engine for "Students like me"'
    else: 
        label = '"Shortest time to graduate" function'
    # 
    # Need to add a dismiss function
    _to_be_implemented(q, label)

######################################################################
#################  COURSE SCHEDULING FUNCTIONS  ######################
######################################################################

## old find_prerequisites from 

# note: renamed 'prerequisite' to 'prerequisites' to follow changes in the db table

def handle_prerequisites(course_list):
    # Create a dictionary to store courses by their name for easy lookup
    courses_dict = {course['name']: course for course in course_list}
    
    # Iterate over the course list to handle prerequisites
    for course in course_list:
        # Check if the course has prerequisites
        if course.get('pre', ''):
            # Split the prerequisites string into individual courses
            prerequisites = course['pre'].split('&')
            
            # Iterate over the prerequisites
            for prereq_group in prerequisites:
                prereq_group = prereq_group.strip()
                
                # Split the prerequisites group into individual prerequisites
                prereqs = prereq_group.split('|')
                
                # Initialize a list to store prerequisite information for each branch
                branch_prereqs_info = []
                
                # Iterate over the prerequisites in the group
                for prereq_name in prereqs:
                    prereq_name = prereq_name.strip()
                    
                    # Check if the prerequisite is not already in the course list
                    if prereq_name not in courses_dict:
                        # Call update_prerequisites function to get information for the prerequisite
                        prereq_info = update_prerequisites(prereq_name)
                        
                        # Add the prerequisite to the branch_prereqs_info list
                        if prereq_info:
                            branch_prereqs_info.append(prereq_info)
                    else:
                        # If the prerequisite is already in the course list, find its index
                        prereq_index = course_list.index(courses_dict[prereq_name])
                        
                        # Add the prerequisite information to the branch_prereqs_info list
                        branch_prereqs_info.append(course_list[prereq_index])
                
                # Insert the branch_prereqs_info into the course_list before the current course
                if branch_prereqs_info:
                    course_list.insert(course_list.index(course), branch_prereqs_info)
    
    return course_list

## Need to update this

def schedule_courses_old(courses, periods, max_courses_default, max_credits_default):
    scheduled_courses = []

    for course in courses:
        while True:
            prerequisites_scheduled = all(pre_course.id in scheduled_courses for pre_course in course.pre)

            if prerequisites_scheduled:
                period_index = find_period_index(course, periods, scheduled_courses)

                if period_index is not None:
                    periods[period_index]['courses'].append(course)
                    scheduled_courses.append(course.id)
                    break
                else:
                    # Add a new period with default values and try scheduling again
                    previous_id = periods[-1]['id'] if periods else 0
                    new_period = {"id": previous_id + 1,
                                  "max_courses": max_courses_default,
                                  "max_credits": max_credits_default,
                                  "previous": previous_id,
                                  "courses": []}
                    periods.append(new_period)

            else:
                # Iterate through prerequisites first
                for pre_course in course.pre:
                    if pre_course.id not in scheduled_courses:
                        # Schedule the prerequisite course first
                        schedule_courses([pre_course], periods, max_courses_default, max_credits_default)
                
                # After scheduling prerequisites, retry scheduling the current course
                continue

    return periods

def update_courses(course, new_period, previous_period, courses, periods, max_courses_default, max_credits_default):
    # Remove the course from its previous period
    previous_period_index = previous_period - 1
    if course in periods[previous_period_index]['courses']:
        periods[previous_period_index]['courses'].remove(course)
    
    # Try to schedule the course in the new period
    new_period_index = new_period - 1
    scheduled_courses = []
    while True:
        prerequisites_scheduled = all(pre_course.id in scheduled_courses for pre_course in course.pre)

        if prerequisites_scheduled:
            if sum(course.credits for course in periods[new_period_index]['courses']) + course.credits <= periods[new_period_index]['max_credits']:
                if all(pre_course.id in scheduled_courses and
                        scheduled_courses.index(pre_course.id) <= periods[new_period_index]['previous']
                        for pre_course in course.pre):
                    periods[new_period_index]['courses'].append(course)
                    scheduled_courses.append(course.id)
                    break
                else:
                    # Move the course to the earliest possible period based on prerequisites
                    earliest_period = max(pre_course.id in scheduled_courses and
                                          scheduled_courses.index(pre_course.id) + 1
                                          for pre_course in course.pre)
                    print(f"Cannot move to period {new_period}: Prerequisites not met. Moving to period {earliest_period} instead.")
                    update_courses(course, earliest_period, new_period, courses, periods, max_courses_default, max_credits_default)
                    return
            else:
                print(f"Cannot move to period {new_period}: Max credits exceeded. Moving other courses forward.")
                move_courses_forward(new_period_index, periods, scheduled_courses)
                continue
        else:
            print(f"Cannot move to period {new_period}: Prerequisites not met.")
            return

    # Cascade changes from the new period onwards
    for i in range(new_period_index + 1, len(periods)):
        for scheduled_course in periods[i]['courses']:
            update_courses(scheduled_course, i + 1, i, courses, periods, max_courses_default, max_credits_default)

    return periods

def move_courses_forward(period_index, periods, scheduled_courses):
    # Find courses in the current period that can be moved forward
    movable_courses = [course for course in periods[period_index]['courses'] if
                       not any(course.id in pre_course.id for pre_course in scheduled_courses)]

    if not movable_courses:
        # If all courses are prerequisites for other courses, move the last one forward
        movable_courses = [periods[period_index]['courses'][-1]]

    # Move the first movable course forward to the next period
    if movable_courses:
        course_to_move = movable_courses[0]
        next_period_index = period_index + 1
        if next_period_index < len(periods):
            periods[next_period_index]['courses'].append(course_to_move)
            scheduled_courses.append(course_to_move.id)
            periods[period_index]['courses'].remove(course_to_move)
            print(f"Moved {course_to_move.name} forward to period {next_period_index + 1}.")
            # Recursively check if more courses can be moved forward
            move_courses_forward(period_index + 1, periods, scheduled_courses)
    else:
        print("No movable courses found.")

    return

    #############################################################################
    ## keycloak implementation code found in utils.py goes here after updating ##
    #############################################################################
    
    ##keycloak_implemented = False
    ###### KEYCLOAK CODE ##############
    ## temporary until keycloak login fully implemented
    ##    if keycloak_implemented:
    ##        #Decode the access token without verifying the signature
    ##        #Connects SSO to our user and student_info tables
    ##        user_details = jwt.decode(q.auth.access_token, options={"verify_signature": False})
    ##
    ##        q.user.username = user_details['preferred_username']
    ##        q.user.name = user_details['name']
    ##        q.user.firstname = user_details['given_name']
    ##        q.user.lastname = user_details['family_name']
    ##
    ## check whether user is in the sqlite3 db
    ## if so, get role and id
    ## if not, add user to db as a new student
    ##        q.user.user_id, q.user.role_id = find_or_add_user(q)
    ##    else:
    ##        # fake it for now

def generate_schedule_old(course_list, periods):
    '''
    '''
    schedule = []
    max_credits_by_term_year = {}
    
    # Iterate over locked courses to update periods and max_credits_by_term_year
    # (i.e., show what scheduling availability remains after considering locked courses)
    for course in course_list:
        if course.get('locked', False):
            term_year = (course['term'], course['year'])
            session = course['session']
            
            # Find the corresponding period
            for period in periods:
                if (period['term'], period['year'], period['session']) == (course['term'], course['year'], course['session']):
                    if period['max_courses_remaining'] > 0:
                        period['max_courses_remaining'] -= 1
                        
                        # Update max_credits_by_term_year
                        if term_year not in max_credits_by_term_year:
                            max_credits_by_term_year[term_year] = period['max_credits']
                        else:
                            max_credits_by_term_year[term_year] -= course['credits']
                        
                        # Add the locked course to the schedule
                        schedule.append({
                            'seq': len(schedule) + 1,
                            'name': course['name'],
                            'term': course['term'],
                            'year': course['year'],
                            'session': course['session'],
                            'locked': True
                        })
                        
                    else:
                        print(f"Unable to assign locked course '{course['name']}' to period {period}.")
                    break  # Exit the inner loop once the corresponding period is found
    
    # Iterate over unlocked courses to schedule them
    for course in course_list:
        if not course.get('locked', False):
            assigned = False
            
            # Iterate over periods to find an appropriate slot
            for period in periods:
                term_year = (period['term'], period['year'])
                
                if period['max_courses_remaining'] > 0 and max_credits_by_term_year[term_year] >= course['credits']:
                    # Add the course to the schedule
                    schedule.append({
                        'seq': len(schedule) + 1,
                        'name': course['name'],
                        'term': period['term'],
                        'year': period['year'],
                        'session': period['session'],
                        'locked': False
                    })
                    
                    # Update period information
                    period['max_courses_remaining'] -= 1
                    max_credits_by_term_year[term_year] -= course['credits']
                    
                    assigned = True
                    break  # Exit the inner loop once a slot is found
            
            if not assigned:
                print(f"Unable to assign unlocked course '{course['name']}' to any period.")
    
    return schedule


def generate_schedule_df_old(course_df, periods_df):
    '''
    Generate a schedule based on course list dataframe and periods dataframe.
    
    Parameters:
    course_df (pd.DataFrame): DataFrame containing course information.
    periods_df (pd.DataFrame): DataFrame containing periods information.
    
    Returns:
    list of dict: Scheduled courses.

    Note: the input dataframe has a column 'name' rather than 'course' (for convenience with d3 function)
    to do: change all 'name' to 'course' after fixing student_progress_d3_view
    '''
    schedule = []
    max_credits_by_term_year = {}
    
    # Iterate over locked courses to update periods and max_credits_by_term_year
    for idx, row in course_df[course_df['locked'] == 1].iterrows():
        term_year = (row['term'], row['year'])
        session = row['session']
        
        # Find the corresponding period
        for period_idx, period in periods_df.iterrows():
            if (period['term'], period['year'], period['session']) == (row['term'], row['year'], row['session']):
                if periods_df.at[period_idx, 'max_courses'] > 0:
                    periods_df.at[period_idx, 'max_courses'] -= 1
                    
                    # Update max_credits_by_term_year
                    if term_year not in max_credits_by_term_year:
                        max_credits_by_term_year[term_year] = period['max_credits']
                    else:
                        max_credits_by_term_year[term_year] -= row['credits']
                    
                    # Add the locked course to the schedule
                    schedule.append({
                        'seq': len(schedule) + 1,
                        'name': row['name'],
                        'term': row['term'],
                        'year': row['year'],
                        'session': row['session'],
                        'locked': True
                    })
                    
                else:
                    print(f"Unable to assign locked course '{row['name']}' to period {period['id']}.")
                break  # Exit the inner loop once the corresponding period is found
    
    # Iterate over unlocked courses to schedule them
    for idx, row in course_df[course_df['locked'] == 0].iterrows():
        assigned = False
        
        # Iterate over periods to find an appropriate slot
        for period_idx, period in periods_df.iterrows():
            term_year = (period['term'], period['year'])
            
            if periods_df.at[period_idx, 'max_courses'] > 0 and max_credits_by_term_year.get(term_year, 0) >= row['credits']:
                # Add the course to the schedule
                schedule.append({
                    'seq': len(schedule) + 1,
                    'name': row['name'],
                    'term': period['term'],
                    'year': period['year'],
                    'session': period['session'],
                    'locked': False
                })
                
                # Update period information
                periods_df.at[period_idx, 'max_courses'] -= 1
                max_credits_by_term_year[term_year] -= row['credits']
                
                assigned = True
                break  # Exit the inner loop once a slot is found
        
        if not assigned:
            print(f"Unable to assign unlocked course '{row['name']}' to any period.")
    
    return pd.DataFrame(schedule)
