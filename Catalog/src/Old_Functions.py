
##########################################################
####################  HOME PAGE ##########################
##########################################################

def create_program_selection_card(location='horizontal', width='60%'):
    """
    Create the program selection card
    """
    card = ui.form_card(
        box=ui.box(location, width=width),
        #name='program_selection',
        #title='Select a UMGC Program',
        #caption='Choose an option to explore UMGC programs',
        #category='Program Selection',
        #icon='Education',
        items=[
            ui.text_xl(content='**Select a UMGC Program**'),
            ui.link(label='Option 1: Explore programs on your own', path='/#program'),
            ui.link(label='Option 2: Select a program based on your skills', path='/#skills'),
            ui.link(label='Option 3: Select a program based on your interests', disabled=True),
            ui.link(label='Option 4: Select a program that finished your degree the quickest', disabled=True)
        ]
    )
    return card

