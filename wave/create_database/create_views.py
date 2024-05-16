import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

# student_info_view used by utils.populate_student_info
drop_view('student_info_view')
create_view_query = '''
    CREATE VIEW student_info_view AS
        SELECT 
            a.user_id, 
            b.firstname || ' ' || b.lastname AS fullname,
            c.label AS resident_status, 
            a.app_stage_id,
            d.stage as app_stage,
            e.label AS student_profile,
            a.transfer_credits, 
            a.financial_aid,
            a.program_id
        FROM 
            student_info a
        LEFT JOIN
            users b
        ON
            a.user_id = b.id
        LEFT JOIN
            resident_status c
        ON
            a.resident_status_id=c.id
        LEFT JOIN
            app_stage d
        ON
            a.app_stage_id=d.id
        LEFT JOIN
            student_profile e
        ON
            a.student_profile_id=e.id
'''
c.execute(create_view_query)
conn.commit()

# used by cards.ge_query, templates.ge_query_j
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
        courses b
    ON 
        a.course_id = b.id
'''
c.execute(create_view_query)
conn.commit()

# complete_records_view used by templates.complete_records_query
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
        courses b
    ON 
        a.class_id = b.id
'''
c.execute(create_view_query)
conn.commit()

# templates.complete_student_records_query
drop_view('student_records_view')
create_view_query = '''
    CREATE VIEW student_records_view AS
    SELECT 
        a.user_id,
        a.program_id,
        a.seq,
        a.course,
        a.course_type_id,
        a.completed,
        a.term,
        a.session,
        a.locked,
        b.credits,
        IFNULL(b.title, '') AS title,
        IFNULL(b.description, '') AS description,
        IFNULL(b.prerequisites, '') as prerequisites,
        IFNULL(b.pre, '') as pre,
        IFNULL(b.pre_credits, '') as pre_credits
    FROM 
        student_progress a
    LEFT JOIN 
        courses b
    ON 
        a.course = b.name
'''
c.execute(create_view_query)
conn.commit()

# used by cards.render_program_coursework_table
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
    LEFT JOIN courses b
    	ON a.course = b.name
    LEFT JOIN course_type c
    	ON a.course_type_id = c.id
'''
c.execute(create_view_query)
conn.commit()

# used by cards.area_query and cards.program_query
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

# catalog_program_sequence_view used by get_catalog_program_sequence
drop_view('catalog_program_sequence_view')
create_view_query = '''
	CREATE VIEW catalog_program_sequence_view AS
    SELECT 
        a.program_id,
        a.seq,
        CASE
            WHEN a.course = 'ELECTIVE' THEN 'ELECTIVE'
            WHEN a.course = 'ELECTIVE-2' THEN 'ELECTIVE'
            ELSE a.course
        END AS name,
        c.name as course_type,
        CASE
            WHEN INSTR(c.name, '_') > 0 
            THEN SUBSTR(c.name, 1, INSTR(c.name, '_') - 1)
            ELSE c.name
        END as type,
        CASE
            WHEN a.course IN ('ELECTIVE', 'ELECTIVE-2') THEN
                CASE
                    WHEN a.course = 'ELECTIVE' THEN 3
                    WHEN a.course = 'ELECTIVE-2' THEN 2
                END
            ELSE b.credits
        END AS credits,
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
    LEFT JOIN course_type c
        ON c.id = a.course_type_id
    LEFT JOIN courses b
        ON a.course = b.name
'''
c.execute(create_view_query)
conn.commit()

# used by utils.get_student_progress_d3
drop_view('student_progress_d3_view')
create_view_query = '''
	CREATE VIEW student_progress_d3_view AS
    SELECT 
        a.id,
        a.user_id,
        a.seq,
        a.course as name,
        COALESCE(b.title, '') AS title,
        a.credits, 
        LOWER(c.label) AS course_type,
        CASE
            WHEN INSTR(c.label, ',') > 0 
            THEN LOWER(SUBSTR(c.label, 1, INSTR(c.label, ',') - 1))
            ELSE LOWER(c.label)
        END as type,
        a.completed,
        a.term,
        a.session,
        a.locked,
        COALESCE(b.prerequisites, '') AS prerequisites,
        COALESCE(b.pre, '') AS pre,
        COALESCE(b.pre_credits, '') AS pre_credits,
        COALESCE(b.substitutions, '') AS substitutions,
        COALESCE(b.description, '') AS description
    FROM student_progress a
    LEFT JOIN courses b
        ON a.course = b.name
    LEFT JOIN course_type c
        ON c.id = a.course_type_id
'''
c.execute(create_view_query)
conn.commit()

# Close the connection
conn.close()
