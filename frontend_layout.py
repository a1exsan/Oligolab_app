from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

import frontend_input_invoce
import frontend_orders_tabs

class oligo_syn_form_layout():

    def __init__(self, user_name='test_operator'):

        self.user_name = user_name
        self.start_count = 0
        self.IP_addres = '192.168.0.1'

        self.make_layout()

    def make_layout(self):

        self.frontend_input_invoce = frontend_input_invoce.oligo_orders_form_layout()
        self.frontend_orders_tabs = frontend_orders_tabs.oligo_orders_database_layout()

        layout_dict = {
            'Input invoces': self.frontend_input_invoce.layout,
            'Orders base': self.frontend_orders_tabs.layout,
        }

        layout_list = []
        for key, value in zip(layout_dict.keys(), layout_dict.values()):
            layout_list.append(dbc.Tab(value, label=key))

        self.tabs = dbc.Tabs(layout_list)

        self.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            dbc.Row(dbc.Col(dbc.Alert(f"User: {self.user_name}"
                                      f"     IP adress: {self.IP_addres}"), width='100%')),
            dbc.Row([
                dbc.Col(self.tabs)
            ])
        ])