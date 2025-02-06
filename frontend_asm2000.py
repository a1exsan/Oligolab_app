from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag

from datetime import date
from datetime import datetime


class asm2000_layout():
    def __init__(self):

        map_tab = pd.DataFrame(
            {
                '#': [0],
                'Order id': [0],
                'Position': [''],
                'Name': [''],
                'Sequence': [''],
                'Purif type':[''],
                'Support type':[''],
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
            {"field": "Position", 'editable': True},
            {"field": "Name"},
            {"field": "Sequence", 'editable': True},
            {"field": "Purif type", 'editable': True},
            {"field": "Support type", 'editable': True},
            {"field": "Date"},
            {"field": "Synt number", 'editable': True},
            {"field": "Scale, OE", 'editable': True},
            {"field": "CPG, mg", 'editable': True},
            {"field": "asm Sequence", 'editable': True},
            {"field": "Status", 'editable': True},
            {"field": "Dens, oe/ml", 'editable': True},
            {"field": "Vol, ml", 'editable': True},
            {"field": "Purity, %", 'editable': True},

            {"field": "Do LCMS", 'editable': True},
            {"field": "Done LCMS", 'editable': True},
            {"field": "Do synth", 'editable': True},
            {"field": "Done synth", 'editable': True},
            {"field": "Do cart", 'editable': True},
            {"field": "Done cart", 'editable': True},
            {"field": "Do hplc", 'editable': True},
            {"field": "Done hplc", 'editable': True},
            {"field": "Do paag", 'editable': True},
            {"field": "Done paag", 'editable': True},
            {"field": "Do sed", 'editable': True},
            {"field": "Done sed", 'editable': True},
            {"field": "Do click", 'editable': True},
            {"field": "Done click", 'editable': True},
            {"field": "Do subl", 'editable': True},
            {"field": "Done subl", 'editable': True},
            {"field": "DONE", 'editable': False},
            {"field": "Wasted", 'editable': True}
        ]

        self.map_tab_ = dag.AgGrid(
            id="asm2000-map-tab",
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

        #MAP TAB
        self.map_tab = html.Div([
            dbc.Row([
                dbc.Col(dbc.Alert("ASM 2000 map"), width='100%'),
                dbc.Container(
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("update tab", outline=True, color="secondary",
                                       id='asm2000-update-tab-btn'),
                            dbc.Button("rename pos", outline=True, color="secondary",
                                       id='asm2000-rename-pos-btn'),
                            dbc.Button("change to Alk", outline=True, color="secondary",
                                       id='asm2000-change-alk-btn'),
                            dbc.Button("generate map", outline=True, color="secondary",
                                       id='asm2000-gen-map-btn'),
                            dbc.Button("save_map", outline=True, color="secondary",
                                       id='asm2000-save-map-btn'),
                            #dbc.Button("update analytics", outline=True, color="secondary",
                            #           id='asm2000-update-anal-btn'),
                            dbc.Button("print passport", outline=True, color="secondary",
                                       id='asm2000-print_pass-btn'),
                            dbc.Button("culc click", outline=True, color="secondary",
                                       id='asm2000-culc_click-btn'),
                            dbc.Button("save sequences file", outline=False, color="info",
                                       id='asm2000-save-seq-file-btn'),
                            dcc.Download(id="download-seq-file")
                        ]),
                    ])
                ),
                html.Br(),
                dbc.Col([
                    dcc.Input(placeholder='Enter map name', id='asm2000-map-name', type="text", debounce=True),
                    dcc.Input(placeholder='Enter synthesys number', id='asm2000-map-synt_number', type="text", debounce=True),
                    dcc.DatePickerSingle(
                        id='asm2000-start-date-select',
                        min_date_allowed=date(2024, 1, 1),
                        max_date_allowed=date(2100, 1, 1),
                        initial_visible_month=date(2017, 8, 5),
                        date=datetime.now().date()
                    )
                ]),
                dbc.Row([
                    dbc.Container(dbc.Row([
                                      dbc.Col([
                                          #dcc.Dropdown(['in queue', 'synthesis', 'purification',
                                          #              'formulation', 'finished', 'arhive'], 'in queue',
                                          #             id='asm2000-status-order-selector'),
                                          #dbc.Button("Set status", outline=True, color="secondary",
                                          #           id='asm2000-set-status-btn'),
                                          dbc.Button("update ologomap status", outline=False, color="primary",
                                                     id='asm2000-update-oligomap-status-btn', className="me-1", size='lg'),
                                          dbc.Button("update order status", outline=False, color="success",
                                                     id='asm2000-update-order-status-btn', className="me-1", size='lg'),
                                      ]),
                                      dbc.Row([
                                          dbc.Col([
                                              dbc.Button("_Do lcms_", outline=True, color="success",
                                                         id='set-do-lcms-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do synth_", outline=True, color="success",
                                                         id='set-do-synth-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do cart_", outline=True, color="success",
                                                         id='set-do-cart-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do hplc_", outline=True, color="success",
                                                         id='set-do-hplc-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do paag_", outline=True, color="success",
                                                         id='set-do-paag-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do sed_", outline=True, color="success",
                                                         id='set-do-sed-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do click_", outline=True, color="success",
                                                         id='set-do-click-btn', className="me-1", size='lg'),
                                              dbc.Button("_Do subl_", outline=True, color="success",
                                                         id='set-do-subl-btn', className="me-1", size='lg'),
                                          ])
                                      ]),
                                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Done lcms", outline=True, color="warning",
                                           id='set-done-lcms-btn', className="me-1", size='lg'),
                                dbc.Button("Done synth", outline=True, color="warning",
                                           id='set-done-synth-btn', className="me-1", size='lg'),
                                dbc.Button("Done cart", outline=True, color="warning",
                                           id='set-done-cart-btn', className="me-1", size='lg'),
                                dbc.Button("Done hplc", outline=True, color="warning",
                                           id='set-done-hplc-btn', className="me-1", size='lg'),
                                dbc.Button("Done paag", outline=True, color="warning",
                                           id='set-done-paag-btn', className="me-1", size='lg'),
                                dbc.Button("Done sed", outline=True, color="warning",
                                           id='set-done-sed-btn', className="me-1", size='lg'),
                                dbc.Button("Done click", outline=True, color="warning",
                                           id='set-done-click-btn', className="me-1", size='lg'),
                                dbc.Button("Done subl", outline=True, color="warning",
                                           id='set-done-subl-btn', className="me-1", size='lg'),
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Wasted selection", outline=False, color="danger",
                                           id='asm2000-wasted-status-btn', className="me-1", size='sm')
                            ])
                        ])
                                  ]))
                ]),
                self.map_tab_
            ]),
        ])

        #modifier TAB
        accord_tab = pd.DataFrame(
            {
                'Modification': ['A', 'C', 'G', 'T', '+A', '+C', '+G', '+T', '6FAM', 'Alk', 'R6G', 'HEX'],
                'asm2000 position': ['A', 'C', 'G', 'T', '5', '6', '7', '8', '9', '[10]', '[11]', '[12]'],
                'Conc, g/ml': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                'ul on step, 5mg': [54., 54., 54., 54., 75., 75., 75., 75., 75., 75., 75., 75.],
                'ul on step, 10mg': [60., 60., 60., 60., 60., 60., 60., 60., 60., 60., 60., 60.],
                'Amount 5mg, g': [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                'Amount 5mg, ml': [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                'Amount 10mg, g': [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                'Amount 10mg, ml': [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]
            }
        )

        columnDefs = [
            {"field": "Modification", 'editable': True},
            {"field": "asm2000 position", 'editable': True},
            {"field": "Conc, g/ml", 'editable': True},
            {"field": "ul on step, 5mg", 'editable': True},
            {"field": "ul on step, 10mg", 'editable': True},
            {"field": "Amount 5mg, g"},
            {"field": "Amount 5mg, ml"},
            {"field": "Amount 10mg, g"},
            {"field": "Amount 10mg, ml"}
        ]

        self.accord_tab = dag.AgGrid(
            id="asm2000-accord-tab",
            columnDefs=columnDefs,
            rowData=accord_tab.to_dict("records"),
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

        self.accord_container = html.Div(
            [
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("substract stock", outline=True, color="secondary",
                                       id='asm2000-sub-stock-btn')
                        ]),
                        self.accord_tab
                    ])
             ]
        )

        # MAP TAB
        map_db_tab = pd.DataFrame(
            {
                '#': [0],
                'Map name': [''],
                'Synth number': [''],
                'Date': [''],
                'in progress': [0],
                'Wasted': [0]
            }
        )

        columnDefs = [
            {"field": "#"},
            {"field": "Map name"},
            {"field": "Synth number"},
            {"field": "Date"},
            {"field": "in progress"},
            {"field": "Wasted"},
        ]

        self.map_db_tab = dag.AgGrid(
            id="asm2000-map-list-tab",
            columnDefs=columnDefs,
            rowData=map_db_tab.to_dict("records"),
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

        click_tab = pd.DataFrame(
            {
                'Order id': [''],
                'Position': [''],
                'Dye': [''],
                'amount nmol': [''],
                'sequence': [''],
                'amount oe': [''],
                'react volume, ul': [0.],
                'azide volume, ul': [0.],
                'Cu buffer volume, ul': [0.],
                'activator volume, ul': [0.],
                'water volume, ul': [0.]
            }
        )

        columnDefs = [
            {"field": "Order id"},
            {"field": "Position"},
            {"field": "Dye"},
            {"field": "amount nmol"},
            {"field": "sequence"},
            {"field": "amount oe"},
            {"field": "react volume, ul"},
            {"field": "azide volume, ul"},
            {"field": "Cu buffer volume, ul"},
            {"field": "activator volume, ul"},
            {"field": "water volume, ul"},
        ]

        self.click_tab = dag.AgGrid(
            id="asm2000-click-tab",
            columnDefs=columnDefs,
            rowData=click_tab.to_dict("records"),
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


        # MAP CONTAINER

        self.map_db_tab_container = html.Div(
            [
                dbc.Col([
                    dbc.Button("Update map", outline=True, color="secondary",
                               id='asm2000-update-map'),
                    dbc.Button("Update actual", outline=True, color="secondary",
                               id='asm2000-update-actual-map'),
                    dbc.Button("Load map", outline=True, color="secondary",
                               id='asm2000-load-map'),
                    dcc.Input(placeholder='Enter name, seq or ID', id='asm2000-search-field', type="text",
                              size='50', debounce=True),
                    dbc.Button("Search maps", outline=True, color="secondary",
                               id='asm2000-search-maps-btn')
                ]),
                dbc.Col([
                    self.map_db_tab,
                    self.click_tab
                ]),
                dbc.Button("Delete row", outline=True, color="secondary",
                           id='asm2000-delete-map')
            ]

        )

        self.map_container = html.Div([
            self.map_tab,
            dbc.Col([
                self.accord_container,
                self.map_db_tab_container
            ])

        ])

        pipeline_dict = {}
        field_list = []
        pipeline_dict['#'] = [0]
        pipeline_dict['type'] = ['']
        pipeline_dict['name'] = ['']
        field_list.append({"field": '#',
                           "checkboxSelection": True,
                           "headerCheckboxSelection": True,
                           "headerCheckboxSelectionFilteredOnly": True,
                           })
        field_list.append({"field": 'type'})
        field_list.append({"field": 'name'})
        for i in range(100):
            pipeline_dict[f'col{i + 1}'] = ['']
            field_list.append({"field": f'col{i + 1}', 'editable': True})

        pipline_db_tab = pd.DataFrame(pipeline_dict)

        getRowStyle_pipeline = {
            "styleConditions": [
                {
                    "condition": "params.data.name == 'DEBLOCK'",
                    "style": {"backgroundColor": "#FF9616", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.name == 'OXIDATION'",
                    "style": {"backgroundColor": "#862A16", "color": "#F0F0F0", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.name == 'COUPLING'",
                    "style": {"backgroundColor": "#00CC96", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.name == 'ADDITION'",
                    "style": {"backgroundColor": "#00CC96", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.name == 'CAPPING'",
                    "style": {"backgroundColor": "#F6F926", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.name == 'WASH'",
                    "style": {"backgroundColor": "#19D3F3", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
            ],
            "defaultStyle": {"backgroundColor": "grey", "color": "black"},
        }

        getRowStyle_phases = {
            "styleConditions": [
                {
                    "condition": "params.data.type == 'DEBLOCK'",
                    "style": {"backgroundColor": "#FF9616", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'OXIDATION'",
                    "style": {"backgroundColor": "#862A16", "color": "#F0F0F0", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'COUPLING'",
                    "style": {"backgroundColor": "#00CC96", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'ADDITION'",
                    "style": {"backgroundColor": "#00CC96", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'CAPPING'",
                    "style": {"backgroundColor": "#F6F926", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'WASH'",
                    "style": {"backgroundColor": "#19D3F3", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'TEST'",
                    "style": {"backgroundColor": "#DADADA", "color": "#FF0000", 'fontWeight': 'bold'},
                },
                {
                    "condition": "params.data.type == 'PRIMERS'",
                    "style": {"backgroundColor": "#FF9616", "color": "#0D2A63", 'fontWeight': 'bold'},
                },
            ],
            "defaultStyle": {"backgroundColor": "grey", "color": "black"},
        }

        self.pipline_db_tab = dag.AgGrid(
            id="asm2000-pipeline-protocol-tab",
            getRowStyle=getRowStyle_pipeline,
            columnDefs=field_list,
            rowData=pipline_db_tab.to_dict("records"),
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

        phases_db_tab = pd.DataFrame(
            {
                '#': [0],
                'name': [''],
                'type': [''],
                'description': ['']
            }
        )

        columnDefs = [
            {"field": "#"},
            {"field": "name"},
            {"field": "type"},
            {"field": "description"}
        ]

        self.phases_db_tab = dag.AgGrid(
            id="asm2000-phases-db-tab",
            getRowStyle=getRowStyle_phases,
            columnDefs=columnDefs,
            rowData=phases_db_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "single", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 800, "width": '100%'},
        )

        self.phases_db_tab_pipe = dag.AgGrid(
            id="asm2000-phases-db-tab-pipe",
            getRowStyle=getRowStyle_phases,
            columnDefs=columnDefs,
            rowData=phases_db_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "single", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 800, "width": '100%'},
        )

        self.pipeline_db_tab = dag.AgGrid(
            id="asm2000-pipeline-db-tab",
            getRowStyle=getRowStyle_phases,
            columnDefs=columnDefs,
            rowData=phases_db_tab.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "single", "animateRows": False,
                             "pagination": True,
                             "enterNavigatesVertically": True,
                             "enterNavigatesVerticallyAfterEdit": True,
                             "singleClickEdit": True
                             },
            style={"height": 500, "width": '100%'},
        )

        pipeline_container = html.Div([
            dcc.ConfirmDialog(
                id='asm2000-delete-pipeline-protocol-confirm',
                message='Are you sure you want to continue?',
            ),
            dbc.Row([
                dbc.Col(
                    html.Div([
                        self.phases_db_tab_pipe,
                        dbc.Button('Show content', id='asm2000-show-content-phase-btn-pipe',
                                   outline=False, color="primary", className="me-1"),
                        dbc.Button('Adjast Phase', id='asm2000-add-phase-btn',
                                   outline=False, color="success", className="me-1")
                    ]), width=3),
                dbc.Col(
                    html.Div([
                        dbc.Input(placeholder='Enter pipeline Name', type='text', id='asm2000-pipe-name-db-input'),
                        dbc.Input(placeholder='Enter pipeline description', type='text', id='asm2000-pipe-desc-db-input'),
                        self.pipline_db_tab,
                        dbc.Button('Generate protocol', id='asm2000-generate-protocol-btn',
                                   outline=False, color="primary", className="me-1"),
                        dbc.Button('Save protocol', id='asm2000-save-protocol-btn',
                                   outline=False, color="primary", className="me-1"),
                        dbc.Button('Insert selected phase', id='asm2000-insert-sel-phase-btn',
                                   outline=False, color="success", className="me-1"),
                        dbc.Button('Delete selected block', id='asm2000-delete-sel-block-btn',
                                   outline=False, color="danger", className="me-1")
                    ]), width=6),
                dbc.Col(
                    html.Div([
                        self.pipeline_db_tab,
                        dbc.Button('Show content', id='asm2000-show-pipeline-db-content-btn',
                                   outline=False, color="primary", className="me-1"),
                        dbc.Button('Load protocol', id='asm2000-load-pipeline-db-protocol-btn',
                                   outline=False, color="success", className="me-1"),
                        dbc.Button('Delete protocol', id='asm2000-delete-pipeline-db-protocol-btn',
                                   outline=False, color="danger", className="me-1"),
                        dcc.Textarea(id='asm2000-pipeline-viewer',
                                     style={'width': '100%', 'height': 500})
                    ]), width=3)
            ])
        ])

        phase_maker = dbc.Container(html.Div([
            dbc.Input(placeholder='Enter phase Name', type='text', id='asm2000-phase-name-input'),
            dbc.Input(placeholder='Enter phase description', type='text', id='asm2000-phase-desc-input'),
            dcc.Textarea(id='asm2000-phase-content',
                style={'width': '100%', 'height': 800}),
            dbc.Button('Add to base', id='asm2000-add-to-base-phase-btn',
                       outline=False, color="primary", className="me-1"),
            dbc.Button('Update to base', id='asm2000-update-to-base-phase-btn',
                       outline=False, color="success", className="me-1")
        ]))

        phase_db_show_conteiner = dbc.Row([
            dcc.ConfirmDialog(
                id='asm2000-delete-phase-confirm',
                message='Are you sure you want to continue?',
            ),
            dbc.Col(phase_maker),
            dbc.Col(html.Div([
                self.phases_db_tab,
                dbc.Button('Show content', id='asm2000-show-content-phase-btn',
                           outline=False, color="primary", className="me-1"),
                dbc.Button('Load Phase', id='asm2000-load-from-base-phase-btn',
                           outline=False, color="success", className="me-1"),
                dbc.Button('Delete Phase', id='asm2000-delete-from-base-phase-btn',
                           outline=False, color="danger", className="me-1")
            ]))
        ])

        editor_tabs = dbc.Tabs([
            dbc.Tab(pipeline_container, label='Pipeline Editor'),
            dbc.Tab(phase_db_show_conteiner, label='Phase Maker')
        ])


        self.tabs = dbc.Tabs([
            dbc.Tab(self.map_container, label='asm2000 map'),
            #dbc.Tab(editor_tabs, label='asm2000 Editor')
        ])

        self.layout = html.Div([
            dbc.Row([
                dbc.Col(self.tabs)
            ])
        ])
