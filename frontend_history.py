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
                    self.data_tab,
                    dbc.Input(placeholder='Info', id='hist-data-info-input', type="text", debounce=True)
                ])
            ])
        ])