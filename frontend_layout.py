from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

import frontend_input_invoce
import frontend_orders_tabs
import frontend_asm2000
import frontend_stock
import frontend_view_passport
import frontend_history

class oligo_syn_form_layout():

    def __init__(self, user_name='test_operator'):

        self.user_name = user_name
        self.start_count = 0
        self.IP_addres = '192.168.0.1'

        self.make_layout()

    def make_layout(self):

        self.frontend_input_invoce = frontend_input_invoce.oligo_orders_form_layout()
        self.frontend_orders_tabs = frontend_orders_tabs.oligo_orders_database_layout()
        self.frontend_asm2000 = frontend_asm2000.asm2000_layout()
        self.frontend_stock = frontend_stock.oligo_stock_database_layout()
        self.frontend_passport = frontend_view_passport.passport_tab_view_layout()
        self.frontend_history = frontend_history.oligo_history_layout()

        layout_dict = {
            'Input invoces': self.frontend_input_invoce.layout,
            'Orders base': self.frontend_orders_tabs.layout,
            'Oligomap builder': self.frontend_asm2000.layout,
            'Stock': self.frontend_stock.layout,
            'Passport': self.frontend_passport.layout,
            'Operations history': self.frontend_history.layout,
        }

        layout_list = []
        for key, value in zip(layout_dict.keys(), layout_dict.values()):
            layout_list.append(dbc.Tab(value, label=key))

        self.tabs = dbc.Tabs(layout_list)

        self.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            dbc.Row(dbc.Col(dbc.Alert(f"User: {self.user_name}"
                                      f"     IP adress: {self.IP_addres}"), width='100%')),
            dbc.Row(dbc.Col([
                dbc.Input(placeholder='Enter pincode', type='text', id='pincode-input')])),
            dbc.Row([
                dbc.Col(self.tabs)
            ])
        ])