import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g
import templates
import utils
import pandas as pd

rao_table_columns = [
    ui.table_column(
        name='id',
        label='Id',
        min_width='20px'
    ),
    ui.table_column(
        name='user',
        label='User',
        sortable=True,
        filterable=True,
        searchable=True,
        min_width='100px'
    ),
    ui.table_column(
        name='product',
        label='Product',
        sortable=True,
        filterable=True,
        searchable=True,
        min_width='100px'
    ),
    ui.table_column(
        name='description',
        label='Description',
        cell_type=ui.markdown_table_cell_type(),
        searchable=True
    ),
    ui.table_column(
        name='icon',
        label='Icon',
        cell_type=ui.icon_table_cell_type(),
        min_width='30px'
    ),
    ui.table_column(
        name='picture',
        label='Picture',
        cell_type=ui.markdown_table_cell_type(),
        min_width='50px'
    ),
    ui.table_column(
        name='audio',
        label='Audio',
        cell_type=ui.markdown_table_cell_type(),
        min_width='300px'
    ),
    ui.table_column(
        name='quantity',
        label='Quantity',
        data_type='number',
        sortable=True,
        min_width='95px'
    ),
    ui.table_column(
        name='discount',
        label='Discount',
        cell_type=ui.progress_table_cell_type(),
        sortable=True,
        min_width='80px'
    ),
    ui.table_column(
        name='tags',
        label='Tags',
        cell_type=ui.tag_table_cell_type(
            name='',
            tags=[
                ui.tag(label='Beverage', color='$brown'),
                ui.tag(label='Home', color='$blue'),
                ui.tag(label='Retail', color='$purple'),
                ui.tag(label='Sale', color='$red')
            ]
        ),
        searchable=True
    ),
    ui.table_column(
        name='menu',
        label='Menu',
        cell_type=ui.menu_table_cell_type(
            commands=[
                ui.command(name='view_transaction', label='View Transaction', icon='Shop'),
                ui.command(name='view_image', label='View Image', icon='ImageSearch')
            ]
        ),
        min_width='40px'
    )
]

rao_table_rows = [
    ui.table_row(
        name='0',
        cells=['0', 'Adam', 'Coffee',
               '<b>Product</b>: <i>Coffee</i>\n<b>Category</b>: <i>Beverages</i>', 'CoffeeScript',
               '<center><img src="https://images.unsplash.com/photo-1587049016823-69ef9d68bd44" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/c/coffee01.mp3" type="audio/wav">',
               '1', '0.09', 'Beverage,Sale']
    ),
    ui.table_row(
        name='1',
        cells=['1', 'Sarah', 'Balloons',
               '<b>Product</b>: <i>Balloons</i>\n<b>Category</b>: <i>Home</i>', 'Balloons',
               '<center><img src="https://images.unsplash.com/photo-1574276254982-d209f79d673a" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/b/balloo01.mp3" type="audio/wav">',
               '10', '0.66', 'Home,Sale']
    ),
    ui.table_row(
        name='2',
        cells=['2', 'Adam', 'Television',
               '<b>Product</b>: <i>Television</i>\n<b>Category</b>: <i>Retail</i>', 'TVMonitor',
               '<center><img src="https://images.unsplash.com/photo-1552975084-6e027cd345c2" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/t/televi03.mp3" type="audio/wav">',
               '1', '0', 'Retail']
    ),
    ui.table_row(
        name='3',
        cells=['3', 'Jen', 'Balloons',
               f'<b>Product</b>: <i>Balloons</i>\n<b>Category</b>: <i>Home</i>', 'Balloons',
               '<center><img src="https://images.unsplash.com/photo-1574276254982-d209f79d673a" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/b/balloo01.mp3" type="audio/wav">',
               '3', '0.15', 'Home,Sale']
    )
]

def rao_table(location='middle_horizontal'):
    """
    Card for table.
    """

    #pagination = ui.table_pagination(total_rows=4, rows_per_page=2) if pagination else None

    card = ui.form_card(
        box=location,
        items=[
            ui.table(
                name='transactions',
                columns=rao_table_columns,
                rows=rao_table_rows,
                #pagination=False,
                groupable=True,
                resettable=True,
                downloadable=True,
                events=['page_change'],
                height='520px'
            ),
            ui.buttons(
                items=[
                    #ui.button(
                    #    name='unpaginate' if pagination else 'paginate',
                    #    label='Unpaginate' if pagination else 'Paginate',
                    #    primary=True
                    #),
                    ui.button(name='multiselect', label='Multiselect', primary=True)
                ],
                justify='center'
            )
        ]
    )

    return card

