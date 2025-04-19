from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag


class oligo_solutions_layout():

    def __init__(self):

        tab = pd.DataFrame(
            {
                '#': [],
                'Name': [],
                "Volume, ml": [],
                'Date': [],
                "User": [],
                "Description": [],
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name", 'editable': False},
            {"field": "Volume, ml", 'editable': False},
            {"field": "Date", 'editable': False},
            {"field": "User", 'editable': False},
            {"field": "Description", 'editable': False},
        ]

        self.tab = dag.AgGrid(
            id="solutions-history-tab",
            columnDefs=columnDefs,
            rowData=tab.to_dict("records"),
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

        tab = pd.DataFrame(
            {
                '#': [],
                'Name': [],
                "Composition": [],
                'Description': [],
                "Culculation": []
            }
        )

        columnDefs = [
            {
                "field": "#",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
            {"field": "Name", 'editable': False},
            {"field": "Composition", 'editable': False},
            {"field": "Description", 'editable': False},
            {"field": "Culculation", 'editable': False},
        ]

        self.comp_tab = dag.AgGrid(
            id="solutions-composition-tab",
            columnDefs=columnDefs,
            rowData=tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "single", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 400, "width": '100%'},
        )

        self.layout = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button("Show solutions", outline=False, color="info",
                               id='show-history-solutions-btn', className="me-1", size='lg'),
                ]),
            dbc.Row([
                self.tab,
                dbc.Col([
                    dbc.Input(placeholder='Enter solution volume', type='text', id='solution-vol-prepare-input', value='500'),
                    dbc.Button("Culc selected solution", outline=False, color="success",
                               id='calc-prepare-solutions-btn', className="me-1", size='lg'),
                ]),
                self.comp_tab,
                dbc.Col([
                    dbc.Button("Prepare solution", outline=False, color="warning",
                               id='prepare-solutions-btn', className="me-1", size='lg'),
                    dbc.Button("Delete preparation", outline=False, color="danger",
                            id='delete-solutions-prep-btn', className="me-1", size='lg')
                ]),
            ])
            ])
        ])