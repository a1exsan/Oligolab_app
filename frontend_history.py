from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag

from datetime import date
from datetime import datetime

class oligo_history_layout():

    def __init__(self):

        hist_tab = pd.DataFrame(
            {
                '#': [],
                'User': [],
                "Date": [],
                'Time': [],
                "URL": [],
                'Remote addr': [],
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "User", 'editable': False},
            {"field": "Date", 'editable': False},
            {"field": "Time", 'editable': False},
            {"field": "URL", 'editable': False},
            {"field": "Remote addr", 'editable': False},
        ]

        self.tab = dag.AgGrid(
            id="history-tab",
            columnDefs=columnDefs,
            rowData=hist_tab.to_dict("records"),
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

        hist_data_tab = pd.DataFrame(
            {
                '#': [],
                'User': [],
                "Date": [],
                'Time': [],
                "URL": [],
                "Data json": [],
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "User", 'editable': False},
            {"field": "Date", 'editable': False},
            {"field": "Time", 'editable': False},
            {"field": "URL", 'editable': False},
            {"field": "Data json", 'editable': False},
        ]

        self.data_tab = dag.AgGrid(
            id="history-data-tab",
            columnDefs=columnDefs,
            rowData=hist_data_tab.to_dict("records"),
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

        map_tab = pd.DataFrame(
            {
                '#': [0],
                'Order id': [0],
                'Position': [''],
                'Name': [''],
                'Sequence': [''],
                'Purif type': [''],
                'Support type': [''],
                'Date': [''],
                'Synt number': [''],
                'Scale, OE': [''],
                'CPG, MG': [''],
                'asm Sequence': [''],
                'Status': ['in queue'],
                'Dens, oe/ml': [0.],
                'Vol, ml': [0.3],
                'Purity, %': [50.],

                'Do LCMS': [True],
                'Done LCMS': [False],
                'Do synth': [True],
                'Done synth': [False],
                'Do cart': [True],
                'Done cart': [False],
                'Do hplc': [True],
                'Done hplc': [False],
                'Do paag': [True],
                'Done paag': [False],
                'Do click': [True],
                'Done click': [False],
                'Do sed': [True],
                'Done sed': [False],
                'Do subl': [True],
                'Done subl': [False],
                'DONE': [False],
                'Wasted': [False],
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Order id"},
            {"field": "Position", 'editable': False},
            {"field": "Name"},
            {"field": "Sequence", 'editable': False},
            {"field": "Purif type", 'editable': False},
            {"field": "Support type", 'editable': False},
            {"field": "Date"},
            {"field": "Synt number", 'editable': False},
            {"field": "Scale, OE", 'editable': False},
            {"field": "CPG, mg", 'editable': False},
            {"field": "asm Sequence", 'editable': False},
            {"field": "Status", 'editable': False},
            {"field": "Dens, oe/ml", 'editable': False},
            {"field": "Vol, ml", 'editable': False},
            {"field": "Purity, %", 'editable': False},

            {"field": "Do LCMS", 'editable': False},
            {"field": "Done LCMS", 'editable': False},
            {"field": "Do synth", 'editable': False},
            {"field": "Done synth", 'editable': False},
            {"field": "Do cart", 'editable': False},
            {"field": "Done cart", 'editable': False},
            {"field": "Do hplc", 'editable': False},
            {"field": "Done hplc", 'editable': False},
            {"field": "Do paag", 'editable': False},
            {"field": "Done paag", 'editable': False},
            {"field": "Do sed", 'editable': False},
            {"field": "Done sed", 'editable': False},
            {"field": "Do click", 'editable': False},
            {"field": "Done click", 'editable': False},
            {"field": "Do subl", 'editable': False},
            {"field": "Done subl", 'editable': False},
            {"field": "DONE", 'editable': False},
            {"field": "Wasted", 'editable': False}
        ]

        self.map_tab_show = dag.AgGrid(
            id="history-map-tab-show",
            columnDefs=columnDefs,
            rowData=map_tab.to_dict("records"),
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

        day_result_tab = pd.DataFrame(
            {
                'Date': [''],
                'Time': [''],
                'User': [''],
                'Name': [''],
                'Order id': [''],
                'Synt number': [''],
                'Position': [''],
                'Sequence': [''],
                'Status': [''],
                'Wasted': [False],
                'client': [''],
                'invoce': [''],
            }
        )

        columnDefs = [
            {"field": "Date"},
            {"field": "Time", 'editable':False},
            {"field": "User", 'editable':False},
            {"field": "Name", 'editable': False},
            {"field": "Order id", 'editable': False},
            {"field": "Synt number", 'editable': False},
            {"field": "Position", 'editable': False},
            {"field": "Sequence", 'editable': False},
            {"field": "Status", 'editable': False},
            {"field": "Wasted", 'editable': False},
            {"field": "client", 'editable': False},
            {"field": "invoce", 'editable': False},
        ]

        self.day_result_tab = dag.AgGrid(
            id="history-map-day-result-show",
            columnDefs=columnDefs,
            rowData=day_result_tab.to_dict("records"),
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
            dbc.Row([
                dbc.Col([
                    html.H6("History table", id='hist-tab-label'),
                    dbc.Button("Show history", outline=False, color="info",
                               id='show-history-btn', className="me-1", size='lg'),
                    self.tab
                ]),
                dbc.Col([
                    html.H6("Data history table", id='data-hist-tab-label'),
                    dbc.Button("Show history", outline=False, color="info",
                               id='show-history-data-btn', className="me-1", size='lg'),
                    dbc.Button("Show row data info", outline=True, color="info",
                               id='show-row-data-info-btn', className="me-1", size='lg'),
                    dbc.Button("Show map tab", outline=False, color="success",
                               id='show-map-tab-data-btn', className="me-1", size='lg'),
                    dbc.Button("Show today tab", outline=False, color="warning",
                               id='show-today-results-btn', className="me-1", size='lg'),
                    self.data_tab,
                    dbc.Input(placeholder='Info', id='hist-data-info-input', type="text", debounce=True),
                    dbc.Button("Backup map", outline=True, color="success",
                               id='backup-map-btn', className="me-1", size='lg'),
                ]),
                dbc.Row([
                    self.map_tab_show,
                    self.day_result_tab
                ])
            ])
        ])