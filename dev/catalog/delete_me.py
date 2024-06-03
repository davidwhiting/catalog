from h2o_wave import Q, ui, data
from typing import Optional, List
from utils import add_card


async def page4_1(q):
    add_card(q, 'form', ui.form_card(box='vertical', items=[
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1'),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox1', label='Textbox 1'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step2', label='Next', primary=True),
        ]),
    ]))

async def page4_2(q):
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]

async def page4_3(q):
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]

def example_dialog(q):
    q.page['meta'].dialog = ui.dialog(
        title='Hello!',
        name='my_dialog',
        items=[
            ui.text('Click the X button to close this dialog.'),
        ],
        # Enable a close button (displayed at the top-right of the dialog)
        closable=True,
        # Get notified when the dialog is dismissed.
        events=['dismissed'],
    )


async def serve(q: Q):
    if not q.client.initialized:  # First visit, create an empty form card for our wizard
        q.page['wizard'] = ui.form_card(box='1 1 2 4', items=[])
        q.client.initialized = True

    wizard = q.page['wizard']  # Get a reference to the wizard form
    if q.args.step1:
        wizard.items = [
            ui.text_xl('Wizard - Step 1'),
            ui.text('What is your name?', name='text'),
            ui.textbox(name='nickname', label='My name is...', value='Gandalf'),
            ui.buttons([ui.button(name='step2', label='Next', primary=True)]),
        ]
    elif q.args.step2:
        q.client.nickname = q.args.nickname
        wizard.items = [
            ui.text_xl('Wizard - Step 2'),
            ui.text(f'Hi {q.args.nickname}! How do you feel right now?', name='text'),
            ui.textbox(name='feeling', label='I feel...', value='magical'),
            ui.buttons([ui.button(name='step3', label='Next', primary=True)]),
        ]
    elif q.args.step3:
        wizard.items = [
            ui.text_xl('Wizard - Done'),
            ui.text(
                f'What a coincidence, {q.client.nickname}! I feel {q.args.feeling} too!',
                name='text',
            ),
            ui.buttons([ui.button(name='step1', label='Try Again', primary=True)]),
        ]
    else:
        wizard.items = [
            ui.text_xl('Wizard Example'),
            ui.text("Let's have a conversation, shall we?"),
            ui.buttons([ui.button(name='step1', label='Of course!', primary=True)]),
        ]

    await q.page.save()





'''
'type', 'part', 'credits', 'course'

'arts', 1, 3, False
'arts', 2, 3, False

'beh',  1, 3, False
'beh',  1, 3, False

'bio',  1, 4, False
'bio',  2, 3, False

'comm', 1, 3, True
'comm', 2, 3, True
'comm', 3, 3, False
'comm', 4, 3, False

'math', 1, 3, False
'res',  1, 

'''

#ge = q.user.student_info['ge']
#ge_summary['ge']
#
#    if row:
#        card = add_card(q, 'major_dashboard', ui.form_card(
#            box=box,
#            items=[
#                #ui.text(title + ': Credits', size=ui.TextSize.L),
#                ui.text('Credits', size=ui.TextSize.L),
#                ui.stats(
#                    items=[
#                        ui.stat(
#                            label='Major',
#                            value=str(row['major']),
#                            #caption='Credits',
#                            icon='Trackers',
#                            icon_color='#135f96'
#                    )]
#                ),
#                ui.stats(
#                    items=[
#                        ui.stat(
#                            label='Required Related',
#                            value=str(row['related_ge'] + row['related_elective']),
#                            #caption='Credits',
#                            icon='News',
#                            icon_color='#a30606'
#                    )]
#                ),
#                ui.stats(
#                    items=[
#                        ui.stat(
#                            label='General Education',
#                            value=str(row['remaining_ge']),
#                            #caption='Remaining GE',
#                            icon='TestBeaker',
#                            #icon_color='#787800'
#                            icon_color='#3c3c43'
#                    )]
#                ),
#                ui.stats(
#                    items=[
#                        ui.stat(
#                            label='Elective',
#                            value=str(row['remaining_elective']),
#                            #caption='Remaining Elective',
#                            icon='Media',
#                            icon_color='#fdbf38'
#                    )]
#                ),
#                ui.separator(),
#                ui.stats(
#                    items=[
#                        ui.stat(
#                            label='TOTAL',
#                            value=str(row['total']),
#                            #caption='Remaining Elective',
#                            icon='Education',
#                            icon_color='#da1a32 '
#                    )]
#                ),
#            ])
#        )




    task_items = [
        #ui.text(title + ': Credits', size=ui.TextSize.L),
        ui.text('Credits', size=ui.TextSize.L),
        #ui.stats(
        #    items=[
        #        ui.stat(
        #            label='Task 1',
        #            value='1',
        #            caption='Personal Information',
        #            icon='Checkbox',
        #            icon_color='#135f96'
        #    )]
        #),
        ui.stats(items=[
            ui.stats(items=[
                ui.stat(
                    label='Task 1',
                    value='1',
                    caption='Personal Information',
                    icon='CheckboxComposite',
                    icon_color='#135f96'
                ),
                ui.stat(
                    label='Task 2',
                    value='2',
                    caption='Program Selected',
                    icon='Checkbox',
                    icon_color='#a30606'
                ),
                ui.stat(
                    label='Task 3',
                    value='3',
                    caption='Courses Added',
                    icon='Checkbox',
                    #icon_color='#787800'
                    icon_color='#3c3c43'
                ),
                ui.stat(
                    label='Task 4',
                    value='4',
                    caption='Schedule Created',
                    icon='Checkbox',
                    icon_color='#fdbf38'
                )
            ])
        ])
    #    ui.separator(),
    #    ui.stats(
    #        items=[
    #            ui.stat(
    #                label='TOTAL',
    #                value=str(row['total']),
    #                #caption='Remaining Elective',
    #                icon='Education',
    #                icon_color='#da1a32 '
    #        )]
    #    ),
    ]
