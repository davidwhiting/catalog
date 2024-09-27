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

def schedule_courses_old_2(prerequisites, course_credits, schedule_slots, locked_courses, corequisites):
    # Process locked courses
    processed_locked_courses = process_locked_courses(locked_courses, schedule_slots)

    # Create a graph of prerequisites
    graph = defaultdict(set)
    all_courses = set()
    for course, prereqs in prerequisites.items():
        graph[course] = set(prereqs)
        all_courses.add(course)
        all_courses.update(prereqs)

    # Create a dictionary for corequisites
    coreq_dict = {}
    for item in corequisites:
        course = item['course']
        coreq_dict[course] = set(item['coreq'])
        for coreq in item['coreq']:
            coreq_dict[coreq] = set([course])

    # Perform topological sort
    ts = TopologicalSorter(graph)
    sorted_courses = list(ts.static_order())

    # Initialize terms based on schedule_slots
    terms = [[] for _ in range(len(schedule_slots))]
    course_to_term = {}

    # Pre-assign locked courses
    for course, term in processed_locked_courses.items():
        terms[term].append(course)
        course_to_term[course] = term
        # Reduce available slots and credits for the term
        schedule_slots[term]['slots'] -= 1
        schedule_slots[term]['credits'] -= course_credits.get(course, 0)

    def find_earliest_available_term(course, start_term=0):
        if course in processed_locked_courses:
            return processed_locked_courses[course]
        if not graph[course]:  # No prerequisites
            return start_term
        prereq_terms = [course_to_term[prereq] for prereq in graph[course] if prereq in course_to_term]
        return max(max(prereq_terms) + 1, start_term) if prereq_terms else start_term

    def can_schedule_in_term(course, term):
        term_info = schedule_slots[term]
        current_courses = len(terms[term])
        current_credits = sum(course_credits.get(c, 0) for c in terms[term])
        course_credits_with_coreqs = course_credits.get(course, 0) + sum(course_credits.get(c, 0) for c in coreq_dict.get(course, []))
        
        return (current_courses + 1 + len(coreq_dict.get(course, [])) <= term_info['slots'] and 
                current_credits + course_credits_with_coreqs <= term_info['credits'])

    # Schedule non-locked courses
    for course in sorted_courses:
        if course in processed_locked_courses or course in course_to_term:
            continue  # Skip courses that are already scheduled

        scheduled = False
        earliest_term = find_earliest_available_term(course)
        
        for term in range(earliest_term, len(terms)):
            if can_schedule_in_term(course, term):
                terms[term].append(course)
                course_to_term[course] = term
                # Schedule corequisites
                for coreq in coreq_dict.get(course, []):
                    if coreq not in course_to_term:
                        terms[term].append(coreq)
                        course_to_term[coreq] = term
                scheduled = True
                break
        
        if not scheduled:
            # Add a new term with default values
            new_term_index = len(terms)
            new_term_info = {
                'slots': 5,
                'credits': 15,
                'term': f'Additional Term {new_term_index + 1}'
            }
            schedule_slots.append(new_term_info)
            terms.append([course])
            course_to_term[course] = new_term_index
            # Schedule corequisites in the new term
            for coreq in coreq_dict.get(course, []):
                if coreq not in course_to_term:
                    terms[new_term_index].append(coreq)
                    course_to_term[coreq] = new_term_index

    # Fill remaining slots with electives
    elective_counter = 1
    for term in range(len(terms)):
        term_info = schedule_slots[term]
        while (len(terms[term]) < term_info['slots'] and 
               sum(course_credits.get(c, 0) for c in terms[term]) + 3 <= term_info['credits']):
            elective = f"ELECTIVE {elective_counter}"
            terms[term].append(elective)
            elective_counter += 1

    return terms

def schedule_courses_old_1(prerequisites, course_credits, schedule_slots, locked_courses, corequisites):
    # Process locked courses
    processed_locked_courses = process_locked_courses(locked_courses, schedule_slots)

    # Create a graph of prerequisites
    graph = defaultdict(set)
    all_courses = set()
    for course, prereqs in prerequisites.items():
        graph[course] = set(prereqs)
        all_courses.add(course)
        all_courses.update(prereqs)

    # Create a dictionary for corequisites
    coreq_dict = {}
    for item in corequisites:
        course = item['course']
        coreq_dict[course] = set(item['coreq'])
        for coreq in item['coreq']:
            coreq_dict[coreq] = set([course])

    # Perform topological sort
    ts = TopologicalSorter(graph)
    sorted_courses = list(ts.static_order())

    # Initialize terms based on schedule_slots
    terms = [[] for _ in range(len(schedule_slots))]
    course_to_term = {}

    # Pre-assign locked courses
    for course, term in processed_locked_courses.items():
        terms[term].append(course)
        course_to_term[course] = term
        # Reduce available slots and credits for the term
        schedule_slots[term]['slots'] -= 1
        schedule_slots[term]['credits'] -= course_credits.get(course, 0)

    def find_earliest_available_term(course, start_term=0):
        if course in processed_locked_courses:
            return processed_locked_courses[course]
        if not graph[course]:  # No prerequisites
            return start_term
        prereq_terms = [course_to_term[prereq] for prereq in graph[course] if prereq in course_to_term]
        return max(max(prereq_terms) + 1, start_term) if prereq_terms else start_term

    def can_schedule_in_term(course, term):
        term_info = schedule_slots[term]
        current_courses = len(terms[term])
        current_credits = sum(course_credits.get(c, 0) for c in terms[term])
        course_credits_with_coreqs = course_credits.get(course, 0) + sum(course_credits.get(c, 0) for c in coreq_dict.get(course, []))
        
        return (current_courses + 1 + len(coreq_dict.get(course, [])) <= term_info['slots'] and 
                current_credits + course_credits_with_coreqs <= term_info['credits'])
    
    def add_new_term():
        new_term_index = len(terms)
        new_term_info = {
            'slots': 5,
            'credits': 15,
            'term': f'Additional Term {new_term_index + 1}'
        }
        schedule_slots.append(new_term_info)
        terms.append([])
        
        # Move "last" term courses to the new term
        last_term_courses = [course for course, term in processed_locked_courses.items() if term == len(terms) - 2]
        for course in last_term_courses:
            terms[new_term_index - 1].remove(course)
            terms[new_term_index].append(course)
            course_to_term[course] = new_term_index
            processed_locked_courses[course] = new_term_index
        
        return new_term_index

    # Schedule non-locked courses
    for course in sorted_courses:
        if course in processed_locked_courses or course in course_to_term:
            continue  # Skip courses that are already scheduled

        scheduled = False
        earliest_term = find_earliest_available_term(course)
        
        for term in range(earliest_term, len(terms)):
            if can_schedule_in_term(course, term):
                terms[term].append(course)
                course_to_term[course] = term
                # Schedule corequisites
                for coreq in coreq_dict.get(course, []):
                    if coreq not in course_to_term:
                        terms[term].append(coreq)
                        course_to_term[coreq] = term
                scheduled = True
                break
        
        if not scheduled:
            # Add a new term and try to schedule in the new term
            new_term_index = add_new_term()
            if can_schedule_in_term(course, new_term_index):
                terms[new_term_index].append(course)
                course_to_term[course] = new_term_index
                # Schedule corequisites in the new term
                for coreq in coreq_dict.get(course, []):
                    if coreq not in course_to_term:
                        terms[new_term_index].append(coreq)
                        course_to_term[coreq] = new_term_index
            else:
                raise ValueError(f"Unable to schedule course {course} even after adding a new term.")

    # Fill remaining slots with electives
    elective_counter = 1
    for term in range(len(terms)):
        term_info = schedule_slots[term]
        while (len(terms[term]) < term_info['slots'] and 
               sum(course_credits.get(c, 0) for c in terms[term]) + 3 <= term_info['credits']):
            elective = f"ELECTIVE {elective_counter}"
            terms[term].append(elective)
            elective_counter += 1

    return terms

def schedule_courses(prerequisites, course_credits, schedule_slots, locked_courses, corequisites):
    # Process locked courses (courses that are locked to specific terms, first, last, etc.)
    processed_locked_courses = process_locked_courses(locked_courses, schedule_slots)

    graph = defaultdict(set)
    all_courses = set()
    for course, prereqs in prerequisites.items():
        graph[course] = set(prereqs)
        all_courses.add(course)
        all_courses.update(prereqs)

    # Identify courses that are not prerequisites for any other course
    not_prerequisite = all_courses - set(course for prereqs in graph.values() for course in prereqs)

    # Create a dictionary for corequisites
    coreq_dict = {}
    for item in corequisites:
        course = item['course']
        coreq_dict[course] = set(item['coreq'])
        for coreq in item['coreq']:
            if coreq in coreq_dict:
                coreq_dict[coreq].add(course)
            else:
                coreq_dict[coreq] = set([course])

    ts = TopologicalSorter(graph)
    sorted_courses = list(ts.static_order())

    terms = [[] for _ in range(len(schedule_slots))]
    course_to_term = {}

    def credits_required(course):
        return course_credits.get(course, 0) + sum(course_credits.get(c, 0) for c in coreq_dict.get(course, []))

    def can_fit_in_term(term, courses):
        term_info = schedule_slots[term]
        current_courses = len(terms[term])
        current_credits = sum(course_credits.get(c, 0) for c in terms[term])
        additional_courses = sum(1 for c in courses if c not in terms[term])
        additional_credits = sum(course_credits.get(c, 0) for c in courses if c not in terms[term])
        
        return (current_courses + additional_courses <= term_info['slots'] and 
                current_credits + additional_credits <= term_info['credits'])

    def move_course_forward(course, from_term):
        for to_term in range(from_term + 1, len(terms)):
            if can_fit_in_term(to_term, [course]):
                terms[from_term].remove(course)
                terms[to_term].append(course)
                course_to_term[course] = to_term
                return True
        return False

    def make_room_in_term(term, needed_slots, needed_credits):
        courses_to_move = []
        for course in terms[term]:
            if course in not_prerequisite and course not in processed_locked_courses:
                courses_to_move.append(course)
                needed_slots -= 1
                needed_credits -= course_credits.get(course, 0)
                if needed_slots <= 0 and needed_credits <= 0:
                    break

        if needed_slots > 0 or needed_credits > 0:
            # If we couldn't find enough non-prerequisite courses, try moving any unlocked course
            for course in terms[term]:
                if course not in processed_locked_courses and course not in courses_to_move:
                    courses_to_move.append(course)
                    needed_slots -= 1
                    needed_credits -= course_credits.get(course, 0)
                    if needed_slots <= 0 and needed_credits <= 0:
                        break

        for course in courses_to_move:
            if not move_course_forward(course, term):
                return False
        return True

    # Schedule locked courses and their corequisites
    for course, term in processed_locked_courses.items():
        courses_to_schedule = [course] + list(coreq_dict.get(course, []))
        if not can_fit_in_term(term, courses_to_schedule):
            needed_slots = len(courses_to_schedule) - (schedule_slots[term]['slots'] - len(terms[term]))
            needed_credits = sum(course_credits.get(c, 0) for c in courses_to_schedule) - (schedule_slots[term]['credits'] - sum(course_credits.get(c, 0) for c in terms[term]))
            if not make_room_in_term(term, needed_slots, needed_credits):
                raise ValueError(f"Unable to make room for locked course {course} and its corequisites in term {term}")
        
        for c in courses_to_schedule:
            if c not in terms[term]:
                terms[term].append(c)
                course_to_term[c] = term

    # Schedule remaining courses
    for course in sorted_courses:
        if course in course_to_term:
            continue

        courses_to_schedule = [course] + list(coreq_dict.get(course, []))
        scheduled = False
        for term in range(len(terms)):
            if can_fit_in_term(term, courses_to_schedule):
                for c in courses_to_schedule:
                    if c not in course_to_term:
                        terms[term].append(c)
                        course_to_term[c] = term
                scheduled = True
                break
        
        if not scheduled:
            raise ValueError(f"Unable to schedule course {course} and its corequisites")

    # Fill remaining slots with electives
    elective_counter = 1
    for term in range(len(terms)):
        term_info = schedule_slots[term]
        while (len(terms[term]) < term_info['slots'] and 
               sum(course_credits.get(c, 0) for c in terms[term]) + 3 <= term_info['credits']):
            elective = f"ELECTIVE {elective_counter}"
            terms[term].append(elective)
            elective_counter += 1

    return terms

# Example usage remains the same as before

import pandas as pd
from graphlib import TopologicalSorter
from collections import defaultdict

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

# Example usage
courses = ['MATH 100', 'MATH 200', 'PHYS 100', 'PHYS 200', 'CHEM 100', 'CHEM 200', 'CHEM 201', 'BIO 300', 'COMP 300', 'LIBS 100', 'CAPS 421']
prerequisites = {
    'MATH 200': ['MATH 100'],
    'PHYS 200': ['MATH 100', 'PHYS 100'],
    'CHEM 200': ['CHEM 100'],
    'BIO 300': ['CHEM 200'],
    'COMP 300': ['MATH 200', 'PHYS 200']
}
course_credits = {
    'MATH 100': 3, 'MATH 200': 3, 'PHYS 100': 4, 'PHYS 200': 4,
    'CHEM 100': 4, 'CHEM 200': 3, 'CHEM 201': 2, 'BIO 300': 3,
    'COMP 300': 4, 'LIBS 100': 1, 'CAPS 421': 3
}
corequisites = {
    'CHEM 200': ['CHEM 201']
}
locked_courses = {
    'LIBS 100': 'first',
    'CAPS 421': 'last',
    'CHEM 200': 'Fall 2026'
}

schedule_slots = [
    {'slots': 4, 'credits': 12, 'term': 'Fall 2025'},
    {'slots': 3, 'credits': 10, 'term': 'Spring 2026'},
    {'slots': 0, 'credits': 0, 'term': 'Summer 2026'},  # Internship
    {'slots': 5, 'credits': 16, 'term': 'Fall 2026'},
    {'slots': 4, 'credits': 13, 'term': 'Spring 2027'}
]

# Create initial schedule DataFrame
schedule_df = create_schedule_dataframe(courses, prerequisites, course_credits, corequisites, locked_courses)

# Schedule courses
scheduled_df = schedule_courses(schedule_df, schedule_slots)

# Display the resulting schedule
print(scheduled_df)