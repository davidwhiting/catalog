### Functions that utilize the Topological Sorter algorithm for scheduling

## Add a new term with appropriate next term structure
##

from graphlib import TopologicalSorter
from collections import defaultdict

def process_locked_courses(locked_courses, schedule_slots):
    processed_locked_courses = {}
    for course, term in locked_courses.items():
        if isinstance(term, int):
            processed_locked_courses[course] = term
        elif term.lower() == 'first':
            processed_locked_courses[course] = 0
        elif term.lower() == 'last':
            processed_locked_courses[course] = len(schedule_slots) - 1
        else:
            # Search for term by name
            for i, slot in enumerate(schedule_slots):
                if slot['term'] == term:
                    processed_locked_courses[course] = i
                    break
            else:
                raise ValueError(f"Term '{term}' not found in schedule_slots")
    return processed_locked_courses

# Example usage remains the same as before

def create_schedule_dataframe(courses, prerequisites, course_credits, corequisites, locked_courses):
    data = []
    for course in courses:
        data.append({
            'course': course,
            'credits': course_credits.get(course, 0),
            'prerequisites': ','.join(prerequisites.get(course, [])),
            'corequisites': ','.join(corequisites.get(course, [])),
            'locked': locked_courses.get(course, None),
            'scheduled_term': None
        })
    return pd.DataFrame(data)

def schedule_courses_new(schedule_df, schedule_slots):
    # Convert DataFrame to necessary data structures
    prerequisites = {row['course']: row['prerequisites'].split(',') if row['prerequisites'] else []
                     for _, row in schedule_df.iterrows()}
    course_credits = dict(zip(schedule_df['course'], schedule_df['credits']))
    corequisites = {row['course']: row['corequisites'].split(',') if row['corequisites'] else []
                    for _, row in schedule_df.iterrows()}
    locked_courses = {row['course']: row['locked'] for _, row in schedule_df.iterrows() if pd.notna(row['locked'])}

    # Existing scheduling logic (modified to update DataFrame)
    # ... [Most of the existing scheduling logic remains the same] ...

    # Update scheduled_term in DataFrame
    for course, term in course_to_term.items():
        schedule_df.loc[schedule_df['course'] == course, 'scheduled_term'] = term

    return schedule_df

### Example usage
##courses = ['MATH 100', 'MATH 200', 'PHYS 100', 'PHYS 200', 'CHEM 100', 'CHEM 200', 'CHEM 201', 'BIO 300', 'COMP 300', 'LIBS 100', 'CAPS 421']
##prerequisites = {
##    'MATH 200': ['MATH 100'],
##    'PHYS 200': ['MATH 100', 'PHYS 100'],
##    'CHEM 200': ['CHEM 100'],
##    'BIO 300': ['CHEM 200'],
##    'COMP 300': ['MATH 200', 'PHYS 200']
##}
##course_credits = {
##    'MATH 100': 3, 'MATH 200': 3, 'PHYS 100': 4, 'PHYS 200': 4,
##    'CHEM 100': 4, 'CHEM 200': 3, 'CHEM 201': 2, 'BIO 300': 3,
##    'COMP 300': 4, 'LIBS 100': 1, 'CAPS 421': 3
##}
##corequisites = {
##    'CHEM 200': ['CHEM 201']
##}
##locked_courses = {
##    'LIBS 100': 'first',
##    'CAPS 421': 'last',
##    'CHEM 200': 'Fall 2026'
##}
##
##schedule_slots = [
##    {'slots': 4, 'credits': 12, 'term': 'Fall 2025'},
##    {'slots': 3, 'credits': 10, 'term': 'Spring 2026'},
##    {'slots': 0, 'credits': 0, 'term': 'Summer 2026'},  # Internship
##    {'slots': 5, 'credits': 16, 'term': 'Fall 2026'},
##    {'slots': 4, 'credits': 13, 'term': 'Spring 2027'}
##]
##
### Create initial schedule DataFrame
##schedule_df = create_schedule_dataframe(courses, prerequisites, course_credits, corequisites, locked_courses)
##
### Schedule courses
##scheduled_df = schedule_courses(schedule_df, schedule_slots)
##
### Display the resulting schedule
##print(scheduled_df)

##
## There is one more type of prerequisite that we need to account for. Some courses are required within the first x number of credits, for instance, Writing 112 (WRTG 112) is required within the first 24 credits. A few are required by 'Within the first 6 credits', those we can easily translate into 'lock in first term', but within the first 24 or within the first 30 credits are a little more difficult. Let's call the variable 'prereq_credits' with 'prereq_credits=24' means within the first 24 credits. How can we account for this in our scheduling code? (Note: these may be GE courses, not just required courses)


import pandas as pd
from graphlib import TopologicalSorter
import sqlite3

def get_major_requirements(major_name):
    # TODO: Implement SQLite query to get major requirements
    # This is a placeholder that you can replace with actual database query later
    conn = sqlite3.connect('university_database.db')
    cursor = conn.cursor()
    # Example query (you'll need to adjust this based on your actual database schema)
    cursor.execute("""
        SELECT courses, required_ge, required_electives
        FROM major_requirements
        WHERE major_name = ?
    """, (major_name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'name': major_name,
            'courses': result[0].split(','),
            'required_ge': result[1].split(','),
            'required_electives': result[2].split(',')
        }
    else:
        raise ValueError(f"Major {major_name} not found in database")

def categorize_courses(courses_df, major_courses, required_ge, required_electives):
    def categorize(course):
        if course in major_courses:
            return 'Major'
        elif course in required_ge:
            return 'Required GE'
        elif course in required_electives:
            return 'Required Elective'
        else:
            return 'Elective'
    
    courses_df['category'] = courses_df['course'].apply(categorize)
    return courses_df

def determine_course_level(course_name):
    try:
        return int(course_name.split()[1][0]) * 100
    except:
        return 0  # Default level if unable to determine

def earliest_year_for_course(course_level, course_category):
    if course_category in ['Major', 'Required GE', 'Required Elective']:
        return (course_level // 100) - 1
    else:
        return 0  # Electives can be taken any year

def group_courses_by_prereq_chain(df):
    # Group courses into chains of prerequisites
    chains = {}
    for _, course in df.iterrows():
        if course['prerequisites']:
            key = tuple(sorted(course['prerequisites'].split(',')))
            if key in chains:
                chains[key].append(course['course'])
            else:
                chains[key] = [course['course']]
        else:
            chains[('no_prereqs',)] = chains.get(('no_prereqs','), []) + [course['course']]
    return chains

def schedule_required_courses(df, schedule_slots):
    required_df = df[df['category'].isin(['Major', 'Required GE', 'Required Elective'])]
    chains = group_courses_by_prereq_chain(required_df)
    
    scheduled_courses = []
    for chain_key, courses in chains.items():
        if chain_key == ('no_prereqs',):
            scheduled_courses.extend(courses)
        else:
            ts = TopologicalSorter({course: df.loc[df['course'] == course, 'prerequisites'].iloc[0].split(',') 
                                    for course in courses if df.loc[df['course'] == course, 'prerequisites'].iloc[0]})
            scheduled_courses.extend(list(ts.static_order()))
    
    # Assign courses to terms based on level and available slots
    for course in scheduled_courses:
        course_data = df.loc[df['course'] == course].iloc[0]
        earliest_year = earliest_year_for_course(course_data['level'], course_data['category'])
        for term in range(earliest_year * 3, len(schedule_slots)):  # 3 terms per year
            if len(schedule_slots[term]['courses']) < schedule_slots[term]['slots']:
                schedule_slots[term]['courses'].append(course)
                df.loc[df['course'] == course, 'scheduled_term'] = term
                break
    
    return df

def schedule_electives(df, schedule_slots, total_credits_required):
    scheduled_credits = df['credits'].sum()
    elective_counter = 1
    
    for term in range(len(schedule_slots)):
        while len(schedule_slots[term]['courses']) < schedule_slots[term]['slots'] and scheduled_credits < total_credits_required:
            elective = f'ELECTIVE {elective_counter}'
            schedule_slots[term]['courses'].append(elective)
            new_row = pd.DataFrame({
                'course': [elective],
                'credits': [3],
                'prerequisites': [''],
                'corequisites': [''],
                'category': ['Elective'],
                'level': [0],
                'scheduled_term': [term]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            scheduled_credits += 3
            elective_counter += 1
    
    return df

def build_schedule(courses_df, major_name, total_credits_required, schedule_slots):
    # Get major requirements
    major = get_major_requirements(major_name)
    
    # Categorize courses
    courses_df = categorize_courses(courses_df, major['courses'], major['required_ge'], major['required_electives'])
    
    # Add level to courses
    courses_df['level'] = courses_df['course'].apply(determine_course_level)
    
    # Schedule required courses
    schedule_df = schedule_required_courses(courses_df, schedule_slots)
    
    # Schedule electives
    final_schedule_df = schedule_electives(schedule_df, schedule_slots, total_credits_required)
    
    return final_schedule_df

# Example usage
courses_df = pd.DataFrame({
    'course': ['CHEM 101', 'CHEM 102', 'MATH 101', 'PHYS 101', 'ENGL 201', 'FILM 250'],
    'credits': [4, 4, 3, 4, 3, 3],
    'prerequisites': ['', 'CHEM 101', '', '', '', ''],
    'corequisites': ['', '', '', '', '', '']
})

schedule_slots = [
    {'term': 'Fall 2025', 'slots': 4, 'courses': []},
    {'term': 'Spring 2026', 'slots': 4, 'courses': []},
    {'term': 'Fall 2026', 'slots': 4, 'courses': []},
    {'term': 'Spring 2027', 'slots': 4, 'courses': []},
    {'term': 'Fall 2027', 'slots': 4, 'courses': []},
    {'term': 'Spring 2028', 'slots': 4, 'courses': []}
]

final_schedule = build_schedule(courses_df, 'Chemistry', 120, schedule_slots)

# Display the final schedule
for term in schedule_slots:
    print(f"{term['term']}: {', '.join(term['courses'])}")