
######################################################################
####################  STANDARD WAVE CARDS  ###########################
######################################################################

#############################################################
####################  Initialize Functions ##################
#############################################################

## Note: moved initialize_app, initialize_user, initialize_client functions
## to app.py to avoid circular import references between utils.py and cards.py

######################################################################

def initialize_ge():
    '''
    Initialize General Education tracking for undergraduate students.
    '''
    ge = {
        'arts': {
            '1': None,
            '2': None
        },
        'beh': {
            '1': None,
            '2': None
        },
        'bio': {
            '1a': None,
            '1b': None,
            '1c': None,
            '2': None
        },
        'comm': {
            '1': 'WRTG 111',
            '2': 'WRTG 112',
            '3': None,
            '4': None
        },
        'math': None,
        'res': {
            '1': None,
            '2': 'LIBS 150',
            '3': None,
            '3a': None,
            '3b': None,
            '3c': None
        }
    }
    return ge

def reset_program(q):
    '''
    When program is changed, multiple variables need to be reset
    '''
    q.user.student_info['menu']['program'] = None
    q.user.student_info['program_id'] = None
    q.user.student_info['df']['required'] = None
    q.user.student_info['df']['schedule'] = None
    q.user.student_info['degree_program'] = None

    q.page['dropdown'].menu_program.value = None
    # reset program choices
    q.page['dropdown'].menu_program.choices = None

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

async def get_student_progress_d3(q):
    query = 'SELECT * FROM student_progress_d3_view WHERE user_id = ?'
    df = await get_query_df(q.user.conn, query, params=(q.user.student_info['user_id'],))
    return df

async def get_choices(timedConnection, query, params=()):
    rows = await get_query(timedConnection, query, params)
    choices = [ui.choice(name=str(row['name']), label=row['label']) for row in rows]
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

def generate_periods(start_term='SPRING 2024', years=8, max_courses=3, max_credits=15, summer=False, sessions=[1,3], as_df=True):
    '''
    A periods structure is a list of dictionaries (or a Pandas dataframe) containing information about terms and sessions,
    into which we will place classes when scheduling.

    Parameters:

    start_term: first term classes are to be scheduled into
    years: number of years to create periods for (this can be larger than needed)
    max_courses: maximum number of courses per session
    max_credits: maximum number of credits per term
    summer: whether attending summer (as default)
    sessions: which sessions (1-3) to schedule classes in (excluding summer term, which has only sessions 1 & 2)
    as_df: return results as Pandas dataframe, otherwise return as list of dictionaries

    Output includes 'previous', a value used to determine placement of prerequisites. Because Sessions 1 & 2 and 
    Sessions 2 & 3 overlap, a Session 2 class cannot have a Session 1 prerequisite, it's previous value is 2 (two
    time-slots previous). Similarly, Session 3 cannot have a Session 2 prerequisite, it's previous value is also 2.
    For all others, the 'previous' value is 1.
    
    Note: We create all terms a student could potentially attend and set max_courses=0 and max_credits=0 for periods they
    are not attending.
    '''
    
    # List terms
    terms = ['WINTER', 'SPRING', 'SUMMER', 'FALL']

    # Define the number of sessions for each term
    sessions_per_term = {
        'WINTER': 3,
        'SPRING': 3,
        'SUMMER': 2,
        'FALL': 3
    }

    # Split the start term into the term and the year
    start_term, start_year = start_term.split()

    # Convert the start year to an integer
    start_year = int(start_year)

    # Initialize the schedule and the id
    schedule = []
    id = 1

    # Loop over the next 'years' years
    for year in range(start_year, start_year + years):
        # Loop over each term
        for term in terms:
            # If the year is the start year and the term is before the start term, skip it
            if year == start_year and terms.index(term) < terms.index(start_term):
                continue
            # Loop over each session
            for session in range(1, sessions_per_term[term] + 1):
                # Set max_courses=0 and max_credits=0 if (term='SUMMER' and summer==False)
                if term=='SUMMER': 
                    if not summer:
                        max_courses_value = 0
                        max_credits_value = 0
                    else:
                        max_courses_value = max_courses
                        # only 2 sessions in summer, adjust max_credits accordingly
                        max_credits_value = 2*int(np.floor(max_credits/3))
                
                # Set max_courses=0 and max_credits=0 if session not in sessions
                else:
                    if session not in sessions:
                        max_courses_value = 0
                        max_credits_value = 0
                    else: # spring, fall, winter
                        max_courses_value = max_courses
                        max_credits_value = max_credits
                       
                # Calculate previous value
                # 
                previous = 1 if session == 1 else 2
 
                # Add the entry to the schedule
                schedule.append({
                    'id': id,
                    'term': term,
                    'session': session,
                    'year': year,
                    'max_courses': max_courses_value,
                    'max_credits': max_credits_value,
                    'previous': previous
                })
                # Increment the id
                id += 1
    # either return as a dataframe or as a list of dictionaries
    if as_df:
        return pd.DataFrame(schedule)
    else:
        return schedule

def update_periods(periods, condition, update_values):
    '''
    Update the 'periods' structure. Will return a DataFrame if a DataFrame is input,
    otherwise will return a list of dictionaries.

    periods: a list of dictionaries or a DataFrame with periods information returned from 'generate_periods'

    Example usage
    # Update max_courses for SPRING 2024 to 0
    update_periods(periods, "term == 'SPRING' and year == 2024", {"max_courses": 0})
    '''

    # Check whether input periods is a DataFrame
    if isinstance(periods, pd.DataFrame):
        return_as_list = False
    else:
        periods = pd.DataFrame(periods)
        return_as_list = True
    
    # Apply conditions
    mask = periods.eval(condition)
    
    # Update values
    for key, value in update_values.items():
        periods.loc[mask, key] = value

    # Convert DataFrame back to a list of dictionaries
    if return_as_list:
        return periods.to_dict(orient='records')
    else:
        return periods

# note: renamed 'prerequisite' to 'prerequisites' to follow changes in the db table

def prepare_d3_data(df, start_term='SPRING 2024'):
    green = '#3b8132'
    blue = '#135f96'
    red = '#a30606'
    yellow = '#fdbf38'
    def set_colors(row):
        if row['type'] == 'general':
            return pd.Series([green, 'white'])
        elif row['type'] == 'major':
            return pd.Series([blue, 'white'])
        # hack: fix the following 3 elifs
        elif row['type'] == 'required,elective':
            row['type'] = 'required'
            return pd.Series([red, 'white'])
        elif row['type'] == 'required,general':
            row['type'] = 'required'
            return pd.Series([red, 'white'])
        elif row['type'] == 'required':
            return pd.Series([red, 'white'])
        elif row['type'] == 'elective':
            return pd.Series([yellow, 'black'])
        else:
            return pd.Series(['white', 'black'])  # default colors

    def generate_header_data(start_semester, num_periods, data_df = df):
        seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
        semester_data = []
        start_season, start_year = start_semester.split(' ')
        start_year = int(start_year)
        season_index = seasons.index(start_season)
        year = start_year
        period = 0

        while period < num_periods:
            for j in range(season_index, len(seasons)):
                semester_data.append(f'{seasons[j]} {year}')
                period += 1

                # Break the loop when i equals num_periods
                if period == num_periods:
                    break

            # Reset the season index to start from 'WINTER' for the next year
            season_index = 0
            year += 1

        df = pd.DataFrame(semester_data, columns=['term'])
        df['width'] = df['term'].apply(lambda x: 190 if 'SUMMER' in x else 260)
        df['offset'] = df['term'].apply(lambda x: 2 if 'SUMMER' in x else 3)
        df['fontsize'] = '14px'
        df['description'] = ''
        df['space'] = 40
        df['xpos'] = df['width'] + df['space']

        x0 = 10
        # Calculate the cumulative sum of 'xpos'
        df['x'] = df['xpos'].cumsum()
        df['x'] = df['x'].shift(1)
        df.loc[0, 'x'] = 0
        df['x'] = df['x'] + x0
        df['y'] = 10
        df['color'] = 'lightgray'
        df['textcolor'] = 'black'
        df['period'] = np.arange(1, num_periods+1)

        df.drop
        # Sum credits per period and convert to a DataFrame
        total_credits = data_df.groupby('period')['credits'].sum().sort_index()
        total_credits_df = total_credits.reset_index()

        df = pd.merge(df, total_credits_df, on='period', how='inner')
        df['name'] = df['term']
        df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'

        return df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 
                   'fontsize', 'period', 'name', 'credits', 'description']]

    # Prepare data for the D3 figure

    max_period = max(df['period'])
    headers = generate_header_data(start_term, max_period)

    df['description'] = df['prerequisites']
    df['width'] = 120
    # Calculate 'x' column
    df = pd.merge(df, headers[['period','x']], on='period', how='left')
    df['x'] += 70*(df['session']-1)

    # Calculate 'y' column
    df = df.sort_values(by=['period', 'session', 'seq' ])
    df['y_row'] = df.groupby('period').cumcount() + 1
    df['y'] = 70 + 45 * (df['y_row'] - 1)

    # Create rectangle colors
    df[['color', 'textcolor']] = df.apply(set_colors, axis=1)

    # Set text offset multiplier to 1 and text fontsize
    df['offset'] = 1
    df['fontsize'] = '12px'
    df['printname'] = df['name'] + ' (' + df['credits'].astype(str) + ')'
    
    df = df[['x', 'y', 'width', 'printname', 'color', 'textcolor', 'offset', 'fontsize', 'period', 'session', 'type', 'name', 'credits', 'description']]

    return df, headers

def generate_schedule(course_list, periods):
    schedule = []
    max_credits_by_term_year = {}
    
    # Iterate over locked courses to update periods and max_credits_by_term_year
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
                            'course': course['name'],
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
                        'course': course['name'],
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
