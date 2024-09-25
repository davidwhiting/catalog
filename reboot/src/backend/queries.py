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
