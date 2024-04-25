import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

drop_view('student_records_view_old')
create_view_query = '''
    CREATE VIEW student_records_view_old AS
    SELECT 
        a.seq as seq,
        a.student_info_id as student_info_id,
        a.name as name,
        a.credits as credits,
        a.type as type,
        a.completed as completed,
        a.period as period,
        a.session as session,
        a.prerequisite as prerequisite,
        IFNULL(b.title, '') AS title,
        IFNULL(b.description, '') AS description,
        IFNULL(b.prerequisites, '') as prereq_full
    FROM 
        student_progress a
    LEFT JOIN 
        classes b
    ON 
        a.name = b.name
'''
c.execute(create_view_query)
conn.commit()

drop_view('ge_view')
create_view_query = '''
    CREATE VIEW ge_view AS
    SELECT 
        a.id,
        a.general_education_requirements_id as ge_id,
        b.name,
        b.title,
        b.credits,
        b.description,
        b.pre,
        b.pre_credits,
        a.note
    FROM 
        general_education a
    LEFT JOIN 
        classes b
    ON 
        a.course_id = b.id
'''
c.execute(create_view_query)
conn.commit()

drop_view('complete_records_view')
create_view_query = '''
    CREATE VIEW complete_records_view AS
    SELECT 
        a.seq,
        a.name,
        a.program_id,
        a.class_id,
        a.course_type_id,
        b.title,
        b.description,
        b.prerequisites
    FROM 
        program_sequence a
    JOIN 
        classes b
    ON 
        a.class_id = b.id
'''
c.execute(create_view_query)
conn.commit()

drop_view('student_records_view')
create_view_query = '''
    CREATE VIEW student_records_view AS
    SELECT 
        a.seq,
        a.student_info_id,
        a.name,
        a.credits,
        a.type,
        a.completed,
        a.prerequisite,
        IFNULL(b.title, '') AS title,
        IFNULL(b.description, '') AS description,
        IFNULL(b.prerequisites, '') as prerequisites,
        IFNULL(b.pre, '') as pre_classes,
        IFNULL(b.pre_credits, '') as pre_credits
    FROM 
        student_progress a
    LEFT JOIN 
        classes b
    ON 
        a.name = b.name
'''
c.execute(create_view_query)
conn.commit()

drop_view('program_requirements_view')
create_view_query = '''
    CREATE VIEW program_requirements_view AS 
    SELECT
    	a.id,
    	a.program_id,
    	b.id as course_id,
    	c.label as course_type,
    	a.course,
    	b.title,
    	a.substitutions,
    	b.credits,
    	b.pre,
    	b.pre_credits,
    	b.description
    FROM program_requirement_courses a
    LEFT JOIN classes b
    	ON a.course = b.name
    LEFT JOIN course_type c
    	ON a.course_type_id = c.id
'''
c.execute(create_view_query)
conn.commit()

drop_view('major_table_view')
create_view_query = '''
    CREATE VIEW major_table_view AS
    SELECT 
        a.id,
        b.program_id,
        a.course, 
        a.course_type AS type,
        a.course_type_id,
        a.title,
        a.credits,
        a.description,
        a.pre,
        a.pre_credits,
        a.substitutions
     FROM program_requirements_view a
     JOIN program_requirements b ON a.program_requirements_id = b.id
'''
c.execute(create_view_query)
conn.commit()

drop_view('menu_all_view')
create_view_query = '''
	CREATE VIEW menu_all_view AS
	SELECT 
		a.menu_degree_id,
		b.name AS degree_name,
		a.menu_area_id,
		c.name AS area_name,
		a.program_id,
		d.name AS program_name
	FROM 
		menu_programs_by_areas a,
		menu_degrees b,
		menu_areas c,
		programs d
	WHERE 
		a.menu_degree_id = b.id
		AND a.menu_area_id = c.id
		AND a.program_id = d.id
'''
c.execute(create_view_query)
conn.commit()


drop_view('catalog_program_sequence_view')
create_view_query = '''
	CREATE VIEW catalog_program_sequence_view AS
    SELECT 
        a.program_id,
        a.seq, 
        a.course AS name,
        c.name as course_type,
        CASE
            WHEN INSTR(c.name, '_') > 0 
            THEN SUBSTR(c.name, 1, INSTR(c.name, '_') - 1)
            ELSE c.name
        END as type,
        b.credits,
        b.title,
        0 AS completed,
        0 AS term,
        0 AS session,
        0 AS locked,
        b.pre,
        b.pre_credits, 
        b.substitutions,
        b.description
    FROM 
        catalog_program_sequence a
    LEFT JOIN
        course_type c
    ON
        c.id = a.course_type_id
    LEFT JOIN
        classes b
    ON
        a.course = b.name
'''
c.execute(create_view_query)
conn.commit()


drop_view('student_progress_d3_view')
create_view_query = '''
	CREATE VIEW student_progress_d3_view AS
    SELECT 
        a.id,
        a.user_id,
        a.seq, 
        a.name,
        COALESCE(b.title, '') AS title,
        a.credits,
        a.course_type,
        a.type,
        a.completed,
        a.term,
        a.session,
        a.locked,
        a.prerequisites,
        COALESCE(b.pre, '') AS pre,
        COALESCE(b.pre_credits, '') AS pre_credits,
        COALESCE(b.substitutions, '') AS substitutions,
        COALESCE(b.description, '') AS description
    FROM 
        student_progress_d3 a
    LEFT JOIN
        classes b
    ON
        a.name = b.name
'''
c.execute(create_view_query)
conn.commit()


# Close the connection
conn.close()
