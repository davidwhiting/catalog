import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

################################################################
# "App stage" table (for students)
# Keep track of where users are in the app stage
# (allow them to review and go back if needed)
# 
# 1: new
# 2: personalized (whether they are at the student profile stage, 
#        not whether they have answered everything.)
# 3: program chosen (whether they have selected a major)
#        building a program from scratch, adding GE, electives, minors, etc. 
#        will be tracked elsewhere
# 4: schedule created 

app_stage = [
    { 'id': 1, 'stage': 'new' },
    { 'id': 2, 'stage': 'personalized' },
    { 'id': 3, 'stage': 'program chosen' },
    { 'id': 4, 'stage': 'classes selected' },
    { 'id': 5, 'stage': 'schedule created' }
]

drop_table('app_stage', c)
c.execute('''
    CREATE TABLE app_stage (
        id INTEGER PRIMARY KEY,
        stage TEXT
    )
''')

c.executemany('INSERT INTO app_stage VALUES (:id, :stage)', app_stage)
conn.commit()

################################################################
# menu_areas Table

menu_areas = [
    {"id": 1, "name": "Business & Management"},
    {"id": 2, "name": "Cybersecurity"},
    {"id": 3, "name": "Data Analytics"},
    {"id": 4, "name": "Education & Teaching"},
    {"id": 5, "name": "Healthcare & Science"},
    {"id": 6, "name": "IT & Computer Science"},
    {"id": 7, "name": "Liberal Arts & Communications"},
    {"id": 8, "name": "Public Safety"},
]

drop_table('menu_areas',c)
c.execute('''
    CREATE TABLE menu_areas (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

c.executemany('INSERT INTO menu_areas VALUES (:id, :name)', menu_areas)
conn.commit()

################################################################
# menu_degrees Table

menu_degrees = [
    { "id": 1, "name": "Associate's" },
    { "id": 2, "name": "Bachelor's" },
    { "id": 3, "name": "Master's" },
    { "id": 4, "name": "Doctorate" },
    { "id": 5, "name": "Undergraduate Certificate" },
    { "id": 6, "name": "Graduate Certificate"}
]

drop_table('menu_degrees',c)
c.execute('''
    CREATE TABLE menu_degrees (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

c.executemany('INSERT INTO menu_degrees VALUES (:id, :name)', menu_degrees)
conn.commit()


################################################################
# "Menu Programs by Areas" Table
# Recreating menu heirarchy at umgc.edu/compare-programs

drop_table('menu_programs_by_areas',c)
c.execute('''
    CREATE TABLE menu_programs_by_areas (
        id INTEGER PRIMARY KEY,
        menu_area_id INTEGER,
        menu_degree_id INTEGER,
        program_id INTEGER,
        FOREIGN KEY(menu_area_id) REFERENCES menu_areas(id)
        FOREIGN KEY(menu_degree_id) REFERENCES menu_degrees(id)
        FOREIGN KEY(program_id) REFERENCES programs(id)
    )
''')

# Associate's
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Associate's" 
    	AND b.name = 'Liberal Arts & Communications'
    	AND c.name IN ('General Studies')
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Associate's"
        );
''')

# Bachelor's in 'Business & Management'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'Business & Management'
    	AND c.name IN (
            'Accounting', 
            'Business Administration', 
            'Finance', 
            'Human Resource Management', 
            'Management Studies', 
            'Marketing'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

# Bachelor's in 'Cybersecurity'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'Cybersecurity'
    	AND c.name IN ('Cybersecurity Management and Policy', 'Cybersecurity Technology')
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

# Bachelor's in 'Data Analytics'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'Data Analytics'
    	AND c.name IN ('Data Science')
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

# Bachelor's in 'Healthcare & Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'Healthcare & Science'
    	AND c.name IN (
            'Biotechnology',
            'Environmental Health and Safety',
            'Gerontology and Aging Services',
            'Health Services Management',
            'Laboratory Management',
            'Nursing for Registered Nurses',
            'Political Science',
            'Psychology',
            'Social Science'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

## double check "environmental health and safety" 
## it didn't seem to make it in 

# Bachelor's in 'IT & Computer Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'IT & Computer Science'
    	AND c.name IN (
            'Applied Technology',
            'Computer Science',
            'Cybersecurity Technology',
            'Management Information Systems',
            'Software Development and Security',
            'Web and Digital Design'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

# Bachelor's in 'Liberal Arts & Communications'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'Liberal Arts & Communications'
    	AND c.name IN (
            'Communication Studies',
            'East Asian Studies',
            'English',
            'General Studies',
            'Graphic Communication',
            'History',
            'Humanities'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

# Bachelor's in 'Public Safety'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Bachelor's" 
    	AND b.name = 'Public Safety'
    	AND c.name IN (
            'Criminal Justice',
            'Homeland Security',
            'Legal Studies',
            'Public Safety Administration'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Bachelor's"
        );
''')

# Master's in 'Business & Management'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Business & Management'
    	AND c.name IN (
            'Accounting and Financial Management',
            'Acquisition and Contract Management',
            'Business Administration',
            'CyberAccounting',
            'Management: Accounting',
            'Management: Criminal Justice Management',
            'Management: Emergency Management',
            'Management: Financial Management',
            'Management: Homeland Security Management',
            'Management: Human Resource Management',
            'Management: Information Systems and Services',
            'Management: Intelligence Management',
            'Management: Interdisciplinary Studies in Management',
            'Management: Marketing',
            'Management: Nonprofit and Association Management',
            'Management: Project Management',
            'Transformational Leadership'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'Cybersecurity'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Cybersecurity'
    	AND c.name IN (
            'Cloud Computing Systems',
            'Cyber Operations',
            'Cybersecurity Management and Policy',
            'Cybersecurity Technology',
            'Digital Forensics and Cyber Investigation',
            'Information Technology: Information Assurance'  
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'Data Analytics'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Data Analytics'
    	AND c.name IN (
            'Data Analytics',
            'Information Technology: Database Systems Technology'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'Education & Teaching'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Education & Teaching'
    	AND c.name IN (
            'Distance Education and E-Learning',
            'Instructional Technology',
            'Learning Design and Technology',
            'Teaching'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'Healthcare & Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Healthcare & Science'
    	AND c.name IN (
            'Biotechnology: Bioinformatics',
            'Biotechnology: Biosecurity and Biodefense',
            'Biotechnology: Biotechnology Management',
            'Biotechnology: Biotechnology Regulatory Affairs',
            'Environmental Management',
            'Healthcare Administration',
            'Health Information Management and Technology'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'IT & Computer Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'IT & Computer Science'
    	AND c.name IN (
            'Cloud Computing Systems',
            'Information Technology: Database Systems Technology',
            'Information Technology: Homeland Security Management',
            'Information Technology: Informatics',
            'Information Technology: Information Assurance',  
            'Information Technology: Project Management',
            'Information Technology: Software Engineering',
            'Information Technology: Systems Engineering'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'Liberal Arts & Communications'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Liberal Arts & Communications'
    	AND c.name IN (
            'Strategic Communications'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Master's in 'Public Safety'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = "Master's" 
    	AND b.name = 'Public Safety'
    	AND c.name IN (
            'Management: Homeland Security Management',
            'Management: Intelligence Management'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == "Master's"
        );
''')

# Doctorate in 'Business & Management'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Doctorate' 
    	AND b.name = 'Business & Management'
    	AND c.name IN (
            'Business Administration',
            'Management: Community College Policy and Administration'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Doctorate' 
        );
''')

# Doctorate in 'Education & Teaching'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Doctorate' 
    	AND b.name = 'Education & Teaching'
    	AND c.name IN (
            'Management: Community College Policy and Administration'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Doctorate' 
        );
''')

# Undergraduate Certificate in 'Business & Management'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'Business & Management'
    	AND c.name IN (
            'Accounting Foundations',
            'Advanced Management',
            'Decision Support for Business',
            'Digital Marketing',
            'HR People Analytics',
            'Human Resource Management',
            'Leadership and Ethics',
            'Management',
            'Project Management'            
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

# Undergraduate Certificate in 'Cybersecurity'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'Cybersecurity'
    	AND c.name IN (
            'Cyber Threat Hunting'  
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

# Undergraduate Certificate in 'Data Analytics'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'Data Analytics'
    	AND c.name IN (
            'Data Analytics',
            'Machine Learning'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

# Undergraduate Certificate in 'Healthcare & Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'Healthcare & Science'
    	AND c.name IN (
            'Applied Social Sciences',
            'Clinical Mental Health Care',
            'Health Information Management and Data Analytics',
            'Watershed Management'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

# Undergraduate Certificate in 'IT & Computer Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'IT & Computer Science'
    	AND c.name IN (
            'Augmented and Virtual Reality Design',
            'Computer Networking',
            'Cyber Threat Hunting',
            'Digital Design',
            'Management Information Systems',
            'Vulnerability Assessment',
            'Web Design'  
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

# Undergraduate Certificate in 'Liberal Arts & Communications'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'Liberal Arts & Communications'
    	AND c.name IN (
            'American Government and Political Processes',
            'Spanish for Business and the Professions',
            'Women, Gender, and Sexuality Studies'  
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

# Undergraduate Certificate in 'Public Safety'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Undergraduate Certificate' 
    	AND b.name = 'Public Safety'
    	AND c.name IN (
            'Public Safety Executive Leadership'  
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Undergraduate Certificate' 
        );
''')

########################

# Graduate Certificate in 'Business & Management'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Business & Management'
    	AND c.name IN (
			'Accounting Information Security',
			'Acquisition and Contract Management',
			'Leadership and Management',
			'Multicultural Marketing',
			'Project Management',
			'Strategic Human Resource Management'          
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'Cybersecurity'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Cybersecurity'
    	AND c.name IN (
			'Cloud Computing and Networking',
			'Cyber Operations',
			'Cybersecurity Management and Policy',
			'Cybersecurity Technology',
			'Digital Forensics and Cyber Investigation',
			'Information Assurance'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'Data Analytics'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Data Analytics'
    	AND c.name IN (
        	'Business Analytics'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'Education & Teaching'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Education & Teaching'
    	AND c.name IN (
			'Instructional Technology Integration',
			'Learning Design and Technology'          
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'Healthcare & Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Healthcare & Science'
    	AND c.name IN (
			'Bioinformatics',
			'Digital Health Leader',
			'Global Health Management',
			'Long-Term Care Administration'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'IT & Computer Science'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'IT & Computer Science'
    	AND c.name IN (
			'Informatics',
			'Systems Engineering'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'Liberal Arts & Communications'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Liberal Arts & Communications'
    	AND c.name IN (
			'Strategic Communications'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

# Graduate Certificate in 'Public Safety'
c.execute('''
    INSERT INTO menu_programs_by_areas (menu_degree_id, menu_area_id, program_id)
    SELECT 
    	a.id AS menu_degree_id,
    	b.id AS menu_area_id,
    	c.id AS program_id
    FROM
    	menu_degrees a,
    	menu_areas b,
    	programs c
    WHERE
    	a.name = 'Graduate Certificate' 
    	AND b.name = 'Public Safety'
    	AND c.name IN (
        	'Homeland Security Management'
        )
        AND c.degree_id IN (
            SELECT id FROM degrees WHERE type == 'Graduate Certificate' 
        );
''')

conn.commit()

# Close the connection
conn.close()
