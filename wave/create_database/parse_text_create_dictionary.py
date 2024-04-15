import sys
import re

##########################################
# Parse text to create course dictionary #
##########################################

## Regular Expressions

# Course Start and End patterns
course_pattern = re.compile(r'^([A-Z]{3}[A-Z]? \d{3}[A-Z]?) ([A-Z].+?) \((\d(?:–\d)?)\)$')
course_start_pattern = re.compile(r'^([A-Z]{3}[A-Z]? \d{3}[A-Z]?) ([A-Z].+?)$')
course_end_pattern = re.compile(r'^(.+?) \((\d(?:–\d)?)\)$')

# Prerequisites
prerequisite_pattern = re.compile(r'Prerequisites?:\s(.*?)(?=\.\s|\.\))', re.DOTALL)
    
# Recommended
recommended_pattern = re.compile(r'Recommended:\s([^\.]+)\.\s')
    
# Substitutions
substitution_pattern = re.compile(r'may\s+receive\s+credit\s+for\s+only\s+one\s+of\s+the\s+following\s+courses: ')

# Warnings 
warning_pattern = re.compile(r'^\(([^\)]+)\)')

## Functions for creating courses

def create_new_course(name, title, credit):
    course = {
        'name': name.strip(),
        'title': title.strip(),
        'credit': credit.strip(),
        'description': '',
        'prerequisites': '',
        'recommended': '',
        'warnings': '',
        'substitutions': '',
        'pre': '',
        'pre_credits': '',
        'pre_notes': ''
    }
    return course

def update_description(course, sub=substitution_pattern, pre=prerequisite_pattern, 
                       warn=warning_pattern, recd=recommended_pattern):
    description = re.sub(r'\n', '', course['description'])
    # Substitutions
    submatch = sub.search(description)
    if submatch:
        start, end = submatch.span()
        course['substitutions'] = description[end:-1].strip()
    # Prerequisites
    prematch = pre.search(description)
    if prematch:
        course['prerequisites'] = prematch.group(1)
    # Recommended
    recmatch = recd.search(description)
    if recmatch:
        course['recommended'] = recmatch.group(1)
    # Warnings
    warnmatch = warn.search(description)
    if warnmatch:
        course['warnings'] = warnmatch.group(1)
    
    return course

def parse_course_info(text):
    '''
    Logic Overview
    
    A course starts by matching a pattern, either
    
        OneLine = STAT 221 Introduction to Statistics (3)
    or
        TwoLine = STAT 536 A Really Long Description that 
                  Takes Up More than One Line (1-3)
    
    - `course_match` will match OneLine and a new course is created
    - `course_match_start` will match the first line of TwoLine 
      and make the variable `start_course = True`
    - `course_match_end` will match the second line of TwoLine and
      a new course is created. This is checked only if the variable 
      `start_course = True`
    - `course_match` and `course_match_end` will turn on the indicator
      variable `description_on = True`
    - a blank line will set `description_on = False` and indicates
      the end of the course.
    - after a course is ended, it is moved to `prior_course` and the
      description is parsed to populate warnings, prerequisites, and 
      recommended in the course
    '''
    courses = []
    prior_course = None
    current_course = None
    start_course = False
    add_description = False

    for line in text.split('\n'):
        
        course_match = course_pattern.search(line)
        course_match_start = course_start_pattern.search(line)
        course_match_end = course_end_pattern.search(line)

        if start_course:
            # Add the second half of a two-line course title
            if course_match_end:
                course_title2, course_credit = course_match_end.groups()
                course_title = course_title1.strip() + ' ' + course_title2.strip()
                current_course = create_new_course(course_name, course_title, course_credit)
                courses.append(current_course)
                start_course = False
                add_description = True

        elif course_match:
            # If we find a course line, extract information and start a new course
            course_name, course_title, course_credit = course_match.groups()
            current_course = create_new_course(course_name, course_title, course_credit)
            courses.append(current_course)
            start_course = False
            add_description = True

        elif course_match_start:
            course_name, course_title1 = course_match_start.groups()
            start_course = True                    
            
        elif current_course is not None:
            # If we are in the middle of a course, add the line to its description
            if add_description:
                # When the description ends, parse it to fill in prerequisites, 
                # recommended, warnings, and substitutions
                if line == '':
                    add_description = False
                    current_course = update_description(course=current_course)
                else:
                    current_course['description'] += line + '\n'

    return courses

####################
# Read in raw file #
####################

infile = 'tmp_pdf2txt.txt'
with open(infile, 'r') as file:
    # Read the entire content of the file into a string
    text = file.read()

courses = parse_course_info(text)

# Create a dictionary with name as the key
all_classes = {course['name']: course for course in courses}

len(all_classes)

###############################
# Filter out graduate courses #
###############################

# filter out graduate courses
grad_pattern = re.compile(r'([A-Z]{3}[A-Z]? [5-9]\d{2}[A-Z]?)')
classes = {key: value for key, value in all_classes.items() if not grad_pattern.match(key)}

len(classes)

########################
# Iterate over courses #
########################

## Regular expression patterns to extract information from the catalog

class_template = r'([A-Z]{3}[A-Z]? \d{3}[A-Z]?)'
A = class_template

# to filter out graduate courses
grad_template = r'([A-Z]{3}[A-Z]? [5-9]\d{2}[A-Z]?)'
G = grad_template

#######################################################################
## Adding the field 'done' to exclude while editing
## enables us to catch edge cases

def initialize_done(classes):
    # Initialize 'done' items in classes dictionary
    # We will iterate over items that are not done in the future
    
    for class_name, class_info in classes.items():
        prerequisites_text = class_info['prerequisites']
        if prerequisites_text == '':
            class_info['done'] = 1
        else:
            class_info['done'] = 0
    return classes
#######################################################################

def count_done():
    return len([entry for entry in classes.values() if entry['done'] == 1])

# Mark done all classes without prerequisites
classes = initialize_done(classes)
count_done()

##############
# Singletons #
##############

#######################################################################
singleton = re.compile(f'^{A}$')

def mark_all_singles(classes, pattern=singleton):
    # Mark classes with prerequisites done so we don't iterate over them anymore
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                class_info['pre']  = prerequisites_text
                class_info['done'] = 1
    return classes
#######################################################################

# Mark done classes with single prerequisite
classes = mark_all_singles(classes)
count_done()

############################
# Simple Multiple Patterns #
############################

#######################################################################
course_or_list2 = re.compile(f'^{A} or {A}$')
course_or_list2a = re.compile(f'^{A} \(or {A}\)$')
course_or_list3 = re.compile(f'^{A}, {A}, or {A}$')
course_or_list4 = re.compile(f'^{A}, {A}, {A}, or {A}$')
course_or_list5 = re.compile(f'^{A}, {A}, {A}, {A}, or {A}$')

course_and_list2 = re.compile(f'^{A} and {A}$')
course_and_list3 = re.compile(f'^{A}, {A}, and {A}$')
course_and_list4 = re.compile(f'^{A}, {A}, {A}, and {A}$')
course_and_list5 = re.compile(f'^{A}, {A}, {A}, {A}, and {A}$')

def update_all_prerequisites(classes, pattern, type='or'):   
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                groups = match.groups()
                if type == 'or': 
                    replaced_text = f'({ " | ".join(groups) })'
                elif type == 'and':
                    replaced_text = f'({ " & ".join(groups) })'
                class_info['pre'] = replaced_text
                class_info['done'] = 1
                
    return classes
#######################################################################

# Mark done classes with known patterns
classes = update_all_prerequisites(classes, pattern = course_or_list2, type='or')
classes = update_all_prerequisites(classes, pattern = course_or_list2a, type='or')
classes = update_all_prerequisites(classes, pattern = course_or_list3, type='or')
classes = update_all_prerequisites(classes, pattern = course_or_list4, type='or')
classes = update_all_prerequisites(classes, pattern = course_or_list5, type='or')

classes = update_all_prerequisites(classes, pattern = course_and_list2, type='and')
classes = update_all_prerequisites(classes, pattern = course_and_list3, type='and')
classes = update_all_prerequisites(classes, pattern = course_and_list4, type='and')
classes = update_all_prerequisites(classes, pattern = course_and_list5, type='and')

count_done()

##########################
# Writing Class Patterns #
##########################

#######################################################################
writing_patterns = [
    r'^WRTG 112 or equivalent',
    r'^WRTG 112 or equiva-lent',
    r'^A writing course',
    r'^Any writing course',
    r'^Any WRTG course'
]
course_writing = re.compile('|'.join(writing_patterns))

def update_writing(classes, pattern=course_writing):   
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                replaced_text = 'WRTG 112*'
                class_info['pre'] = replaced_text
                class_info['pre_notes'] = 'or equivalent'
                class_info['done'] = 1           
    return classes
#######################################################################

classes = update_writing(classes)
count_done()

#############################
# Foreign Language Patterns #
#############################

#######################################################################
#language_patterns = [
#    f'^{A} or appropriate score on a place',
#    f'^{A} or appropri-ate score on a place'
#]
#course_language = re.compile('|'.join(language_patterns))

language_pattern1 = re.compile(f'^{A} or appropriate score on a place')
language_pattern2 = re.compile(f'^{A} or appropri-ate score on a place')

def update_language(classes, pattern):   
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                replaced_text = match.group(1) + '*'
                class_info['pre'] = replaced_text
                class_info['pre_notes'] = 'placement test'
                class_info['done'] = 1               
    return classes
#######################################################################

classes = update_language(classes,language_pattern1)
classes = update_language(classes,language_pattern2)
count_done()

###########################
# Prior Approval Patterns #
###########################

###############################
#     Complex And/Or Patterns #
###############################

def debug_remaining(done=0, classes=classes):
    for class_name, class_info in classes.items():
        if class_info['done'] == done:
            print (class_name + ':', class_info['prerequisites'])

def update_general_pattern(classes, pattern, replacement_function):   
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                replaced_text = replacement_function(match)
                class_info['pre'] = replaced_text
                class_info['done'] = 1               
    return classes

#######################################################################
prior_pattern = re.compile('(9 credits in the discipline and prior program approval)')

def update_prior_program(classes, pattern=prior_pattern):   
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                class_info['pre_credits'] = 9
                class_info['pre_notes'] = 'prior program approval'
                class_info['done'] = 1         
    return classes
#######################################################################

classes = update_prior_program(classes)
count_done()

#######################################################################
course_and_or_list3 = re.compile(f'^{A} and {A} \(or {A}\)$')
def replacement_function(match):
    return '(' + match.group(1) + ' & (' + match.group(2) + ' | ' + match.group(3) + '))'

classes = update_general_pattern(classes, course_and_or_list3, replacement_function)
count_done()

#######################################################################
course_or_and_list5 = re.compile(f'^{A}, {A}, {A} \(or {A}\), and {A}$')
## Not working, missing something
def replacement_function(match):
    return '(' + match.group(1) + ' & ' + match.group(2) + ' & ' + match.group(5) + ' (' + match.group(3) + ' | ' + match.group(4) + '))'

classes = update_general_pattern(classes, course_or_and_list5, replacement_function)
count_done()
#######################################################################
course_and_or_list3a = re.compile(f'^{A} \(or {A}\) and {A}$')
def replacement_function(match):
    return '((' + match.group(1) + ' | ' + match.group(2) + ') & ' + match.group(3) + ')'

classes = update_general_pattern(classes, course_and_or_list3a, replacement_function)
count_done()

#######################################################################
course_spch = re.compile(r'Any SPCH course or COMM 300')
def replacement_function(match):
    return '(SPCH 100+ | COMM 300)'

classes = update_general_pattern(classes, course_spch, replacement_function)
count_done()

#######################################################################
course_or_pattern1 = re.compile(f'^{A} \(or {A}\) or {A}$')
course_or_pattern2 = re.compile(f'^{A} or {A} \(or {A}\)$')

def replacement_function(match):
    return '(' + match.group(1) + ' | ' + match.group(2) + ' | ' + match.group(3) + ')'

classes = update_general_pattern(classes, course_or_pattern1, replacement_function)
classes = update_general_pattern(classes, course_or_pattern2, replacement_function)
count_done()

#######################################################################
course_nsci = re.compile(r'MATH 105, STAT 200, or a higher MATH or STAT course')
def replacement_function(match):
    return '(MATH 105 | STAT 200 | MATH 300+ | STAT 300+)'

classes = update_general_pattern(classes, course_nsci, replacement_function)
count_done()

#######################################################################
course_span = re.compile(r'Any 300-level SPAN course or appropriate score on a placement test')

def update_spanish(classes, pattern=course_span):   
    for class_name, class_info in classes.items():
        if class_info['done'] == 0:
            prerequisites_text = class_info['prerequisites']
            match = pattern.search(prerequisites_text)
            if match:
                class_info['pre'] = 'SPAN 300+'
                class_info['pre_notes'] = 'placement test'
                class_info['done'] = 1         
    return classes
#######################################################################

classes = update_spanish(classes)
count_done()

#######################################################################
course_or_and_pattern4a = re.compile(f'^{A} \(or {A}\), {A}, or {A}$')
course_or_and_pattern4b = re.compile(f'^{A} \(or {A}\) and {A} \(or {A}\)$')

def replacement_function(match):
    return '((' + match.group(1) + ' | ' + match.group(2) + ') & (' + match.group(3) + ' | ' + match.group(4) + '))'

classes = update_general_pattern(classes, course_or_and_pattern4a, replacement_function)
classes = update_general_pattern(classes, course_or_and_pattern4b, replacement_function)
count_done()

#########################
# Individual edge cases #
#########################

classes['APTC 495'].update({
	'pre_credits': 27, 
	'done': 1})
classes['BEHS 495'].update({ 
	'pre': 'BEHS 300', 
	'pre_notes': 'completion of all requirements for the social science major', 
	'done': 1})
classes['BIOL 230'].update({ 
	'pre': 'BIOL 103', 
	'pre_notes': 'or other introductory biology course with laboratory',
	'done': 1})
classes['BIOL 357'].update({ 
	'pre': '(BIOL 325 | BIOL 300+)',
	'done': 1})
classes['COMM 495'].update({ 
	'pre': '(COMM 300 & COMM 302)', 
	'pre_credits': 9,
	'pre_notes': '9 credits (COMM 300+ | SPCH 300+ | JOUR 300+)',
	'done': 1})
classes['CMIT 320'].update({ 
	'pre': 'CMIT 265',
	'pre_notes': 'or CompTIA Network+ certification',
	'done': 1})
classes['CMIT 424'].update({ 
	'pre': '(CMIT 202 & CMIT 320 & CCJS 321)',
	'pre_notes': 'CMIT 202 (or CompTIA A+ certification), CMIT 320 (or CompTIA Security+ certification)',
	'done': 1})
classes['CMIT 495'].update({ 
	'pre_credits': 27,
	'pre_notes': 'CMIT coursework', 
	'done': 1})
classes['CMSC 498'].update({ 
	'pre_notes': 'Vary according to topic', 
	'done': 1})
classes['CMST 495'].update({ 
	'pre_credits': 24,
	'pre_notes': 'within the major', 
	'done': 1})
classes['CSIA 300'].update({ 
	'pre': '(CMIS 100+ | CMIT 100+ | CMSC 100+ | CMST 100+ | CSIA 100+ | DATA 100+ | IFSM 100+ | SDEV 100+)', 
	'done': 1})
classes['CSIA 310'].update({ 
	'pre': '(IFSM 201 & WRTG 112*)', 
	'done': 1})
classes['DATA 230'].update({ 
	'pre': '(STAT 200 & (MATH 115 | MATH 108))',
	'pre_notes': 'or higher', 
	'done': 1})
classes['ENGL 495'].update({ 
	'pre': '(ENGL 240 & ENGL 303)',
	'pre_credits': 9,
	'pre_notes': 'ENGL 300+', 
	'done': 1})
classes['ENHS 495'].update({ 
	'pre': '(ENHS 305 & ENHS 330 & ENHS 340)',
	'pre_credits': 30,
	'pre_notes': 'ENHS courses',
	'done': 1})
classes['HIST 289'].update({ 
	'pre': 'HIST 1xx',
	'done': 1})
classes['HIST 495'].update({ 
	'pre': '(HIST 289 & HIST 309)', 
	'pre_credits': 21,
	'pre_notes': 'HIST courses',
	'done': 1})
classes['HMLS 495'].update({ 
	'pre_credits': 15,
	'pre_notes': 'FSCN 300+, EMGT 300+, HMLS 300+, or PSAD 300+',
	'done': 1})
classes['HUMN 495'].update({ 
	'pre': '(HUMN 100 & ARTH 300+ & ENGL 300+ & HUMN 300+ & PHIL 300+)', 
	'done': 1})
classes['IFSM 461'].update({ 
	'pre': '(IFSM 311 & (IFSM 330 | CMIS 320)', 
	'done': 1})
classes['PHYS 121'].update({ 
	'pre': '(MATH 108 | MATH 115)', 
	'pre_notes': 'or knowledge of college-level trigonometry', 
	'done': 1})
classes['PSYC 495'].update({ 
	'pre': '(PSYC 100 & PSYC 300)', 
	'pre_notes': 'completion of all require-ments for the psychology major', 
	'done': 1})

debug_remaining()

## check output
#classes['PSYC 495']

##################################
# Save the Dictionary to SQLite3 #
##################################
import sqlite3
conn = sqlite3.connect('UMGC.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE classes (
        id INTEGER PRIMARY KEY,  
        name TEXT,
        title TEXT,
        credits TEXT,
        description TEXT,
        prerequisites TEXT,
        recommended TEXT,
        warnings TEXT,
        substitutions TEXT,
        pre TEXT,
        pre_credits TEXT,
        pre_notes TEXT
    )
''')

# Insert data into the table

i = 0 # add primary key
for class_name, class_info in classes.items():
    i += 1
    c.execute('''
        INSERT INTO classes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        i,
        class_info['name'],
        class_info['title'],
        class_info['credit'],
        class_info['description'],
        class_info['prerequisites'],
        class_info['recommended'],
        class_info['warnings'],
        class_info['substitutions'],
        class_info['pre'],
        class_info['pre_credits'],
        class_info['pre_notes']
    ))

conn.commit()
conn.close()
