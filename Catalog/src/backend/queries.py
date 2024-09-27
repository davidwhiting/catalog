########################################################
####################  MENU QUERIES  ####################
########################################################

### These queries are used in app.py for menus and  ###
### render_dropdown_menus_horizontal                ###

degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
area_query = '''
    SELECT DISTINCT menu_area_id AS name, area_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ?
'''
program_query_old = '''
    SELECT program_id AS name, program_name AS label
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''
program_query = '''
    SELECT program_id AS name, program_name AS label, disabled
    FROM menu_all_view 
    WHERE menu_degree_id = ? AND menu_area_id = ?
'''

######################################################
####################  GE QUERIES  ####################
######################################################

ge_query = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
    ORDER BY course
'''
ge_query_nopre = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? 
        AND pre='' 
        AND pre_credits=''
    ORDER BY course
'''
ge_credits_query = '''
    SELECT course AS name, course || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=? AND credits=? 
    ORDER BY course
'''
ge_pairs_query = '''
    SELECT 
        course AS name, 
        course || ' & ' || substr(note, 27, 3) || ': ' || title AS label 
    FROM ge_view 
    WHERE ge_id=10 AND credits=3
    ORDER BY course
'''
