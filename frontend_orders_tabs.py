from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from datetime import date
from datetime import datetime

import dash_ag_grid as dag

class oligo_orders_database_layout():

    def __init__(self):

        main_tab = pd.DataFrame(
            {
                '#': [1],
                'Name': [''],
                "5'-end": [''],
                'Sequence': [''],
                "3'-end": [''],
                'Amount, oe': ['5-10'],
                'Purification': ['Cart'],
                'Lenght': [''],
                'status': ['in queue'],
                'input date': [''],
                'output date': [''],
                'client id': [''],
                'order id': ['']
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name", 'editable': True},
            {"field": "5'-end", 'editable': True},
            {"field": "Sequence", 'editable': True},
            {"field": "3'-end", 'editable': True},
            {"field": "Amount, oe", 'editable': True},
            {"field": "Purification", 'editable': True},
            {"field": "Lenght"},
            {"field": "status", 'editable': True},
            {"field": "input date", 'editable': True},
            {"field": "output date", 'editable': True},
            {"field": "order id"},
            {"field": "client id"}
        ]

        self.tab = dag.AgGrid(
            id="orders-tab-database",
            columnDefs=columnDefs,
            rowData=main_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 800, "width": '100%'},
        )

        order_tab = pd.DataFrame({
            '#': [0],
            'invoce': [''],
            'client': [''],
            'input date': [''],
            'out date': [''],
            'number': [0],
            'in queue%': [''],
            'synth%': [''],
            'purif%': [''],
            'formul%': [''],
            'fin%': [''],
            'archived%': [''],
            'status': [''],
            'send': [True]
        })

        columnDefs = [
            {"field": "#"},
            {"field": "invoce"},
            {"field": "client"},
            {"field": "input date"},
            {"field": "out date"},
            {"field": "number"},
            {"field": "in queue%"},
            {"field": "synth%"},
            {"field": "purif%"},
            {"field": "formul%"},
            {"field": "fin%"},
            {"field": "archived%"},
            {"field": "status"},
            {"field": "send", 'editable': True},
        ]

        self.invoce_tab = dag.AgGrid(
            id="invoce-tab-database",
            columnDefs=columnDefs,
            rowData=order_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 800, "width": '100%'},
        )

        self.layout = html.Div([
            dbc.Container(
                html.Div([
                dbc.Row([
                    dbc.Col([
                    dbc.Button("show queue", outline=True, color="secondary",
                               id='show-not-completed'),
                    #dbc.Button("selected to pipeline", outline=True, color="secondary",
                    #           id='to-pipeline-btn'),
                    #dbc.Button("selected to sequences", outline=True, color="secondary",
                    #           id='to-sequences-btn'),
                    dbc.Button("update tab", outline=True, color="secondary",
                                   id='update-outdate-btn')
                    ]),
                    dbc.Col([
                        dbc.Button("add selected to ASM2000", outline=True, color="primary",
                                   id='add-sel-order-to-asm2000-btn'),
                        dbc.Input(placeholder='Number of copies', id='num-orders-copies-input', type="text",
                                  debounce=True)
                    ])
                    ]),
                #dbc.Row([
                    #dbc.Col(
                    #dcc.Dropdown(['POLYGEN_1', 'POLYGEN_2', 'BIOSET96_1'], 'POLYGEN_1',
                    #             id='synthesiser-selector')
                    #),
                    #dbc.Col(
                    #    dcc.DatePickerSingle(
                    #        id='start-date-select',
                    #        min_date_allowed=date(2024, 1, 1),
                    #        max_date_allowed=date(2100, 1, 1),
                    #        initial_visible_month=date(2017, 8, 5),
                    #        date=datetime.now().date()
                    #    ),
                #    )
                #]),
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(['in queue', 'in progress', 'synthesis', 'purification',
                                          'formulation', 'finished', 'arhive'], 'in queue',
                                         id='status-order-selector')
                        ),
                    dbc.Col(
                        dbc.Button("show by status", outline=True, color="secondary",
                                   id='show-orders-by-status-btn')
                    )
                    ])
                ])
            ),
            dbc.Row(self.tab),
            dbc.Col(
                dbc.Button("delete sel rows", outline=True, color="secondary",
                           id='delete-select-rows-btn')
            ),
            dbc.Col([
                dbc.Button("show invoces", outline=False, color="primary",
                       id='show-all-invoces-btn'),
                dbc.Button("show in progress", outline=False, color="secondary",
                           id='show-in-progress-btn'),
                dbc.Button("show invoce content", outline=False, color="primary",
                           id='show-invoce-content-btn'),
                dbc.Button("Print passport", outline=False, color="secondary",
                           id='print-invoce-pass-btn'),
                dbc.Button("Send update", outline=False, color="warning",
                           id='send-update-invoce-btn'),
            ]),
            dbc.Row(self.invoce_tab),
        ])
