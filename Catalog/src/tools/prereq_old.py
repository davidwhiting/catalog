########################################################################
#################  COURSE PREREQUISITE FUNCTIONS  ######################
########################################################################

async def update_prerequisites(timed_connection, prereq_name):
    '''
    Function to update prerequisites. 
    '''
    # Placeholder implementation
    query = '''
    SELECT course AS name, 'elective' as course_type, 'elective' as type, credits, title, 
        0 as completed, 0 as term, 0 as session, 0 as locked, pre, pre_credits, 
        substitutions, description
    FROM courses
    WHERE course = ?
    ''' 
    result = await get_query_dict(timed_connection, query, params=(prereq_name, ))
    if result:
        return result
    else:
        return None

def parse_prerequisites(prereq_string):
    '''
    Parse the prerequisites string and return a list of prerequisite groups.
    Each group contains lists of courses that satisfy the 'or' and 'and' patterns.
    '''
    import re
    prereq_string = prereq_string.strip()
    prereq_string = re.sub(r'\s+', ' ', prereq_string)
    prereq_string = re.sub(r'\(', '', prereq_string)
    prereq_string = re.sub(r'\)', '', prereq_string)
    
    and_groups = prereq_string.split('&')
    prereq_groups = [group.split('|') for group in and_groups]
    
    # Strip whitespace from each course in the groups
    prereq_groups = [[course.strip() for course in group] for group in prereq_groups]
    
    return prereq_groups

### A second approach 

def insert_prerequisite(df, i, name):
    # Recursive function to insert prerequisites
    pre_dict = update_prerequisites(name)
    if pre_dict is not None:
        # Shift rows down
        df.loc[i+2:] = df.loc[i+1:-1].values
        # Insert the prerequisite row
        df.loc[i+1] = pre_dict
        # Check if the inserted prerequisite has its own prerequisites
        insert_prerequisite(df, i+1, pre_dict['name'])

### A Third Approach
### This is old but has some good code in it
def prep_course_list(df):
    '''
    This function takes a DataFrame as input and returns a modified DataFrame where the courses are 
    ordered based on their prerequisites. It handles both “or” and “and” conditions in prerequisites, 
    as well as the ‘*’ and ‘+’ notations.

    Please note that this function assumes that the update_prerequisites function returns a dictionary 
    with keys that match the columns of your DataFrame. 
    '''

    import re

    # Assuming df is the DataFrame and it has columns 'name', 'pre', 'met', and 'where'
    for i, row in df.iterrows():
        if pd.notna(row['pre']):
            pre_courses = [pre.split('&') for pre in row['pre'].split('|')]  # Split prerequisites on '|' and '&'
            met = False
            for pre_group in pre_courses:
                met_group = True
                for pre_course in pre_group:
                    pre_course = pre_course.strip()  # Remove leading/trailing whitespace
                    if '*' in pre_course:
                        pre_course = pre_course.replace('*', '')  # Remove '*' from the course name
                    if '+' in pre_course:
                        course_prefix, course_number = re.match(r'(\D+)(\d+)\+', pre_course).groups()
                        pre_rows = df[(df['name'].str.startswith(course_prefix)) & (df['name'].str.slice(start=len(course_prefix)).astype(int) >= int(course_number))]
                    else:
                        pre_rows = df[df['name'] == pre_course]
                    if not pre_rows.empty:
                        if pre_rows.index[0] > i:
                            # Move the prerequisite row to immediately precede the current row
                            cols = df.columns.tolist()
                            temp = df.loc[pre_rows.index[0], cols].tolist()
                            df.loc[i+2:] = df.loc[i+1:-1].values  # Shift rows down
                            df.loc[i+1] = temp  # Insert the prerequisite row
                    else:
                        # If the prerequisite is not found in the DataFrame, get it and insert it
                        print(f'The prerequisite {pre_course} is not found, it should be inserted!')
                        #insert_prerequisite(df, i, pre_course)
                        met_group = False
                        break  # Exit the loop as soon as one prerequisite is not met
                if met_group:
                    met = True
                    break  # Exit the loop as soon as one group of prerequisites is met
            df.at[i, 'met'] = met
            df.at[i, 'where'] = i - 1  # The prerequisite should be the previous row
    return df

async def handle_prerequisites(timed_connection, course_df):
    '''
    Expand the course list to include necessary prerequisites.

    Group_satisfied approach:

    1. For each group of prerequisites associated with a course, we iterate over each individual 
       prerequisite in the group.
    2. For each prerequisite, we check if it's already present in courses_dict. If it is, then the 
       group is considered satisfied, and we move on to the next group.
    3. If the prerequisite is not present in courses_dict, we perform wildcard (*) and optional (+) 
       matching to check if any existing courses match the pattern. If such a course is found, the 
       group is considered satisfied.
    4. If no existing courses satisfy any prerequisite in the group, we proceed to update and add the 
       missing prerequisites to courses_dict and rows_to_append.

       This approach ensures that we only update and add missing prerequisites if none of the prerequisites 
       in a group are already satisfied by existing courses in courses_dict. If any prerequisite in the 
       group is already satisfied, we skip updating and adding new prerequisites for that group.

    Features:

    1. Recursive Function: The recursive_add_prerequisites function takes a prerequisite name, checks 
       if it's already in courses_dict, and if not, it retrieves its information using update_prerequisites.
    2. Recursion: If the prerequisite has its own prerequisites, recursive_add_prerequisites is called 
       recursively for each of them.
    3. Updating courses_dict and rows_to_append: The function ensures that all necessary prerequisites are 
       added to courses_dict and rows_to_append.
    4. Processing Main Courses: The main loop processes each course with prerequisites, using the recursive 
       function to ensure all prerequisites are included.
    '''

    async def recursive_add_prerequisites(prereq_name, courses_dict, rows_to_append):
        '''
        Recursively add prerequisites to the courses_dict and rows_to_append list.
        '''
        if prereq_name in courses_dict:
            return courses_dict[prereq_name]

        prereq_info = await update_prerequisites(timed_connection, prereq_name)
        if prereq_info:
            prerequisites = parse_prerequisites(prereq_info.get('pre', ''))
            for prereq_group in prerequisites:
                group_satisfied = False
                for sub_prereq_name in prereq_group:
                    sub_prereq_name = sub_prereq_name.strip()
                    if sub_prereq_name in courses_dict:
                        group_satisfied = True
                        break
                    elif sub_prereq_name.endswith('*'):
                        base_name = sub_prereq_name.rstrip('*')
                        if any(existing_course.startswith(base_name) for existing_course in courses_dict):
                            group_satisfied = True
                            break
                    elif sub_prereq_name.endswith('+'):
                        base_name = sub_prereq_name.rstrip('+')
                        if any(existing_course.startswith(base_name) and existing_course > base_name for existing_course in courses_dict):
                            group_satisfied = True
                            break

                if not group_satisfied:
                    for sub_prereq_name in prereq_group:
                        sub_prereq_name = sub_prereq_name.strip()
                        await recursive_add_prerequisites(sub_prereq_name, courses_dict, rows_to_append)

            courses_dict[prereq_name] = prereq_info
            if prereq_info not in rows_to_append:
                rows_to_append.append(prereq_info)
        return prereq_info

    # Filter out rows where 'name' is 'ELECTIVE', 'GENERAL', or an empty string, then set index and convert to dictionary
    courses_dict = course_df[~course_df['name'].isin(['ELECTIVE', 'GENERAL', ''])].set_index('name').to_dict('index')
    rows_to_append = []
    
    # Define filter condition for prerequisites
    filter_condition = (course_df['pre'] != '') & (~course_df['pre'].isna())
    
    for idx, course in course_df[filter_condition].iterrows():
        prerequisites = parse_prerequisites(course['pre'])
        
        for prereq_group in prerequisites:
            # Check if any prerequisite in the group satisfies the condition
            group_satisfied = False
            for prereq_name in prereq_group:
                prereq_name = prereq_name.strip()
                if prereq_name in courses_dict:
                    group_satisfied = True
                    break
                elif prereq_name.endswith('*'):
                    base_name = prereq_name.rstrip('*')
                    if any(existing_course.startswith(base_name) for existing_course in courses_dict):
                        group_satisfied = True
                        break
                elif prereq_name.endswith('+'):
                    base_name = prereq_name.rstrip('+')
                    if any(existing_course.startswith(base_name) and existing_course > base_name for existing_course in courses_dict):
                        group_satisfied = True
                        break
            
            # If no prerequisite in the group is satisfied, update prerequisites
            if not group_satisfied:
                for prereq_name in prereq_group:
                    prereq_name = prereq_name.strip()
                    await recursive_add_prerequisites(prereq_name, courses_dict, rows_to_append)
    
    prereq_df = pd.DataFrame(rows_to_append)
    updated_course_df = pd.concat([prereq_df, course_df]).drop_duplicates(subset='name').reset_index(drop=True)
    return updated_course_df

