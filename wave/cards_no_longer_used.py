#def render_home_cards(q, location='top_horizontal', width='25%'):
#    add_card(q, 'student_guest', ui.wide_info_card(
#        box=ui.box(location, width=width),
#        name='',
#        icon='Contact',
#        title='Guests',
#        caption='Login not required to use this app.'
#    ))
#    add_card(q, 'login',
#        ui.wide_info_card(
#            box=ui.box(location, width=width),
#            name='login',
#            title='Login',
#            caption='User roles: *admin*, *coach*, *student*, *prospect*.',
#            icon='Signin')
#    )
#    add_card(q, 'import',
#        ui.wide_info_card(
#            box=ui.box(location, width=width),
#            name='import',
#            title='Import',
#            caption='Future state: Import UMGC student info.',
#            icon='Import')
#    )
#    add_card(q, 'personalize',
#        ui.wide_info_card(
#            box=ui.box(location, width=width),
#            name='person',
#            title='Personalize',
#            caption='User adds new info or confirms imported info.',
#            icon='UserFollowed')
#    )

#async def render_dropdown_menus_old(q, location='top_horizontal', menu_width='280px'):
#    degree_query = 'SELECT id AS name, name AS label FROM menu_degrees'
#    area_query = '''
#        SELECT DISTINCT menu_area_id AS name, area_name AS label
#        FROM menu_all_view 
#        WHERE menu_degree_id = ?
#    '''
#    program_query = '''
#        SELECT program_id AS name, program_name AS label
#        FROM menu_all_view 
#        WHERE menu_degree_id = ? AND menu_area_id = ?
#    '''
#    card = ui.form_card(
#        box=location,
#        items=[
#            ui.dropdown(
#                name='degree',
#                label='Degree',
#                value=q.client.degree if (q.client.degree is not None) else q.args.degree,
#                trigger=True,
#                width=menu_width,
#                choices=await get_choices(q, degree_query)
#            ),
#            ui.dropdown(
#                name='area_of_study',
#                label='Area of Study',
#                value=q.client.area_of_study if (q.client.area_of_study is not None) else \
#                    q.args.area_of_study,
#                trigger=True,
#                disabled=False,
#                width=menu_width,
#                choices=None if (q.client.degree is None) else \
#                    await get_choices(q, area_query, (q.client.degree,))
#            ),
#            ui.dropdown(
#                name='program',
#                label='Program',
#                value=q.client.program if (q.client.program is not None) else q.args.program,
#                trigger=True,
#                disabled=False,
#                width=menu_width,
#                choices=None if (q.client.area_of_study is None) else \
#                    await get_choices(q, program_query, (q.client.degree, q.client.area_of_study))
#            )
#        ]
#    )
#    return card


async def render_program_table_old(q, df, location='bottom_vertical', cardname='my_test_table', width='100%', ge=False, elective=False):
    '''
    An update of render_major_table to use pandas df directly
    q:
    records:
    '''
    def _render_program_table_group(group_name, record_type, df, collapsed, check=True):
        '''
        group_name: 
        record_type: 
        df: course (Pandas) dataframe
        collapsed:
        check: If True, only return card if # rows > 0
            e.g., we will always return 'MAJOR' but not necessarily 'REQUIRED'
        '''
        # card will be returned if 
        # (1) check == False
        # (2) check == True and sum(rows) > 0
        no_rows = (df['type'].str.upper() == record_type).sum() == 0

        if check and no_rows:
            return None
        else:
            return ui.table_group(group_name, [
                ui.table_row(
                    name=str(row['id']),
                    cells=[
                        row['course'],
                        row['title'],
                        str(row['credits']),
                        #row['description'],
                        row['type'].upper(),
                    ]
                ) for index, row in df.iterrows() if row['type'].upper() == record_type
            ], collapsed=collapsed)
    
    return add_card(q, cardname, ui.form_card(
        box=ui.box(location, height='350px', width=width),
        items=[
            #ui.text(title, size=ui.TextSize.L),
            ui.table(
                name='program_table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='350px',
                columns=[
                    # ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
                    ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300',
                                    cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                                    align='center'),
                    ui.table_column(
                        name='tag',
                        label='Type',
                        min_width='190',
                        filterable=True,
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='menu', label='Menu', max_width='150',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                    ]))
                ],
                groups=[
                    _render_program_table_group(
                        'Required Major Core Courses',
                        'MAJOR',
                        df,
                        False,
                        check=False),
                    # only create if any exist
                    _render_program_table_group(
                        'Required Related Courses/General Education',
                        'REQUIRED,GENERAL',
                        df,
                        True),
                    # only create if any exist
                    _render_program_table_group(
                        'Required Related Courses/Electives',
                        'REQUIRED,ELECTIVE',
                        df,
                        True),
                    #_render_program_table_group(
                    #    'General Education',
                    #    'GENERAL',
                    #    major_records,
                    #    True),
                    #_render_program_table_group(
                    #    'Electives',
                    #    'ELECTIVE',
                    #    major_records,
                    #    True)
            # ui.text(title, size=ui.TextSize.L),
        ])]
    ))

    #student_type = ["Associate", "Bachelor's", "Master's", "Doctorate"]
    #add_card(q, 'student_type_card', ui.form_card(
    #    box=ui.box('middle_horizontal', width='250px'),
    #    items=[
    #        ui.choice_group(
    #            name='student_type',
    #            label='Student Type',
    #            inline=False,
    #            choices=[ui.choice(name=x, label=x) for x in student_type],
    #            value=q.client.student_type if (q.client.student_type is not None) else q.args.student_type,
    #        )
    #    ]
    #))


def render_major_table_group(group_name, record_type, records, collapsed):
    return ui.table_group(group_name, [
        ui.table_row(
            name=str(record['id']),
            cells=[
                record['course'],
                record['title'],
                str(record['credits']),
                #record['description'],
                record['type'].upper(),
            ]
        ) for record in records if record['type'].upper() == record_type
    ], collapsed=collapsed)

async def render_major_table(q, records, location='bottom_vertical', cardname='my_test_table', width='100%', ge=False, elective=False):
    def _render_major_table_group(group_name, record_type, records, collapsed):
        return ui.table_group(group_name, [
            ui.table_row(
                name=str(record['id']),
                cells=[
                    record['course'],
                    record['title'],
                    str(record['credits']),
                    #record['description'],
                    record['type'].upper(),
                ]
            ) for record in records if record['type'].upper() == record_type
        ], collapsed=collapsed)

    return add_card(q, cardname, ui.form_card(
        box=ui.box(location, height='350px', width=width),
        items=[
            #ui.text(title, size=ui.TextSize.L),
            ui.table(
                name='table',
                downloadable=False,
                resettable=False,
                groupable=False,
                height='350px',
                columns=[
                    # ui.table_column(name='seq', label='Seq', data_type='number'),
                    ui.table_column(name='course', label='Course', searchable=False, min_width='100'),
                    ui.table_column(name='title', label='Title', searchable=False, min_width='180', max_width='300',
                                    cell_overflow='wrap'),
                    ui.table_column(name='credits', label='Credits', data_type='number', min_width='50',
                                    align='center'),
                    ui.table_column(
                        name='tag',
                        label='Type',
                        min_width='190',
                        filterable=True,
                        cell_type=ui.tag_table_cell_type(
                            name='tags',
                            tags=[
                                ui.tag(label='ELECTIVE', color='#FFEE58', label_color='$black'),
                                ui.tag(label='REQUIRED', color='$red'),
                                ui.tag(label='GENERAL', color='#046A38'),
                                ui.tag(label='MAJOR', color='#1565C0'),
                            ]
                        )
                    ),
                    ui.table_column(name='menu', label='Menu', max_width='150',
                        cell_type=ui.menu_table_cell_type(name='commands', commands=[
                            ui.command(name='description', label='Course Description'),
                            ui.command(name='prerequisites', label='Show Prerequisites'),
                    ]))
                ],
                groups=[
                    _render_major_table_group(
                        'Required Major Core Courses',
                        'MAJOR',
                        records,
                        True),
                    _render_major_table_group(
                        'Required Related Courses/General Education',
                        'REQUIRED,GENERAL',
                        records,
                        True),
                    _render_major_table_group(
                        'Required Related Courses/Electives',
                        'REQUIRED,ELECTIVE',
                        records,
                        True),
                    #_render_major_table_group(
                    #    'General Education',
                    #    'GENERAL',
                    #    major_records,
                    #    True),
                    #_render_major_table_group(
                    #    'Electives',
                    #    'ELECTIVE',
                    #    major_records,
                    #    True)
            # ui.text(title, size=ui.TextSize.L),
        ])]
    ))

async def render_majors_coursework(q, location='bottom_vertical'):
    '''
    Create major coursework requirement table
    '''
    query = '''
        SELECT 
            id,
            course, 
            course_type as type,
            title,
            credits,
            pre,
            pre_credits,
            substitutions,
            description
        FROM program_requirements_view
        WHERE program_id = ?
    '''
    df = pd.read_sql_query(query, q.user.conn, params=(q.user.program_id,))
    major_records = df.to_dict('records')
    q.user.major_coursework_df = df
    
    await render_major_table(q, major_records, location)

async def render_majors_coursework_new(q, location='bottom_vertical'):
    '''
    Create major coursework requirement table
    '''
    if not q.user.major_coursework_df:
        query = '''
            SELECT 
                id,
                course, 
                course_type as type,
                title,
                credits,
                pre,
                pre_credits,
                substitutions,
                description
            FROM program_requirements_view
            WHERE program_id = ?
        '''
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.program_id,))
        q.user.major_coursework_df = df

    major_records = q.user.major_coursework_df.to_dict('records')    
    await render_major_table(q, major_records, location)

async def render_majors(q, location='middle_vertical', width='100%'):

    async def _render_major_dashboard(q, location=location, width=width):
        '''
        Renders the dashboard with explored majors
        :param q: instance of Q for wave query
        :param location: page location to display
        '''
        title = q.user.degree_program # program name
 
        if q.user.degree == '2':
            # get program summary for bachelor's degrees
            query = 'SELECT * FROM program_requirements WHERE program_id = ?'
            row = await get_query_one(q, query, params=(q.user.program_id,))

            if row:
                return add_card(q, 'major_dashboard', ui.form_card(
                    box=ui.box(location, width=width),
                    items=[
                        ui.text(title + ': Credits', size=ui.TextSize.L),
                        ui.stats(
                            # justify='between',
                            items=[
                                ui.stat(
                                    label='Major',
                                    value=str(row['major']),
                                    caption='Required Core',
                                    icon='Trackers'),
                                ui.stat(
                                    label='Required',
                                    value=str(row['related_ge'] + row['related_elective']),
                                    caption='Required Related',
                                    icon='News'),
                                ui.stat(
                                    label='General Education',
                                    value=str(row['remaining_ge']),
                                    caption='Remaining GE',
                                    icon='TestBeaker'),
                                ui.stat(
                                    label='Elective',
                                    value=str(row['remaining_elective']),
                                    caption='Remaining Elective',
                                    icon='Media'),
                                ui.stat(
                                    label='TOTAL',
                                    value=str(row['total']),
                                    caption='Total Credits',
                                    icon='Education'),
                        ])
                ]))
            #else:
            #    pass
            #    # send a warning
    async def _render_major_coursework(q, location=location):
        '''
        Create major coursework requirement table
        '''
        query = '''
            SELECT 
                id,
                course, 
                course_type as type,
                title,
                credits,
                pre,
                pre_credits,
                substitutions,
                description
            FROM program_requirements_view
            WHERE program_id = ?
        '''
        df = pd.read_sql_query(query, q.user.conn, params=(q.user.program_id,))
        major_records = df.to_dict('records')
        q.user.major_coursework_df = df

        await render_major_table(q, major_records, location)
        #await render_program_table(q, df, location)

    await _render_major_dashboard(q, location=location)
    await _render_major_coursework(q, location=location)

async def render_major_dashboard(q, location='middle_vertical', width='100%'):
    '''
    Renders the dashboard with explored majors
    :param q: instance of Q for wave query
    :param location: page location to display
    '''

    title = q.user.degree_program # program name
 
    if q.user.degree == '2':
        # get program summary for bachelor's degrees
        query = 'SELECT * FROM program_requirements WHERE program_id = ?'
        row = await get_query_one(q, query, params=(q.user.program_id,))

        if row:
            return add_card(q, 'major_dashboard', ui.form_card(
                box=ui.box(location, width=width),
                items=[
                    ui.text(title + ': Credits', size=ui.TextSize.L),
                    ui.stats(
                        # justify='between',
                        items=[
                            ui.stat(
                                label='Major',
                                value=str(row['major']),
                                caption='Required Core',
                                icon='Trackers'),
                            ui.stat(
                                label='Required',
                                value=str(row['related_ge'] + row['related_elective']),
                                caption='Required Related',
                                icon='News'),
                            ui.stat(
                                label='General Education',
                                value=str(row['remaining_ge']),
                                caption='Remaining GE',
                                icon='TestBeaker'),
                            ui.stat(
                                label='Elective',
                                value=str(row['remaining_elective']),
                                caption='Remaining Elective',
                                icon='Media'),
                            ui.stat(
                                label='TOTAL',
                                value=str(row['total']),
                                caption='Total Credits',
                                icon='Education'),
                    ])
            ]))
        #else:
        #    pass
        #    # send a warning



async def render_student_dropdown(q, menu_width, location):
    card = ui.form_card(
        box=ui.box(location),
        items=[
            #ui.separator(label=''),
            ui.text('Select Student', size=ui.TextSize.XL),
            ui.dropdown(
                name='student_selector',
                label='Select Student',
                value=q.client.student_selector if (q.client.student_selector is not None) else q.args.student_selector,
                trigger=True,
                #placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (11,))
            ),
            ui.dropdown(
                name='ge_beh_2',
                label='2. Behavioral and Social Sciences (3 credits)',
                value=q.user.ge_beh_2 if (q.user.ge_beh_2 is not None) else q.args.ge_beh_2,
                trigger=True,
                placeholder='(Select One)',
                width=menu_width,
                choices=await get_choices(q, ge_query, (11,))
            ),
        ]
    )
    return card


########### good through here #############



    #states = [
    #    ('q.app', q.app),
    #    ('q.user', q.user),
    #    ('q.client', q.client),
    #    ('q.events', q.events),
    #    ('q.args', q.args)
    #]
