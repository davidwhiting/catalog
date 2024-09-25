from h2o_wave import ui

APP_NAME = 'Catalog'
REPO_URL = 'https://github.com/davidwhiting/catalog'
ISSUE_URL = f'{REPO_URL}/issues/new?assignees=davidwhiting&labels=bug&template=error-report.md&title=%5BERROR%5D'

UMGC_tags = [
    ui.tag(label='ELECTIVE', color='#fdbf38', label_color='$black'),
    ui.tag(label='REQUIRED', color='#a30606'),
    ui.tag(label='MAJOR', color='#135f96'),
#    ui.tag(label='GENERAL', color='#3c3c43'), # dark gray
#    ui.tag(label='GENERAL', color='#787800'), # khaki   
    ui.tag(label='GENERAL', color='#3b8132', label_color='$white'), # green   
]