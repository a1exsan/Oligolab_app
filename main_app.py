import pandas as pd
from dash import Dash, Input, State, Output, Patch, callback, ctx, dcc, html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from flask import request

import backend

import frontend_layout as frontend

import datetime
from datetime import datetime as ddt

frontend_obj = frontend.oligo_syn_form_layout()
frontend_obj.IP_addres = backend.get_IP_addr()
frontend_obj.make_layout()

orders_data = backend.orders_db(db_IP='127.0.0.1', db_port='8012')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.title= 'OligosApp'
server = app.server
app.layout = frontend_obj.layout

@callback(
    Output(component_id='orders-tab-database', component_property='rowData', allow_duplicate=True),
    Output(component_id='invoce-tab-database', component_property='rowData', allow_duplicate=True),

    Input(component_id='orders-tab-database', component_property='rowData'),
    Input(component_id='invoce-tab-database', component_property='rowData'),
    Input(component_id='invoce-tab-database', component_property='selectedRows'),
    Input(component_id='status-order-selector', component_property='value'),
    Input(component_id='show-orders-by-status-btn', component_property='n_clicks'),
    Input(component_id='show-all-invoces-btn', component_property='n_clicks'),
    Input(component_id='show-in-progress-btn', component_property='n_clicks'),
    Input(component_id='show-invoce-content-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_orders_db_tab(orders_db_data, invoces_rowdata, invoces_selRows, status_selector, show_by_status_btn,
                         show_all_invoces_btn, show_in_progress_btn, shoe_invoce_content_btn):

    triggered_id = ctx.triggered_id

    if triggered_id == 'show-orders-by-status-btn' and show_by_status_btn is not None:
        orders_tab = orders_data.get_orders_by_status(status_selector)
        return orders_tab, invoces_rowdata

    if triggered_id == 'show-all-invoces-btn' and show_all_invoces_btn is not None:
        total_invoces = orders_data.get_all_invoces()
        return orders_db_data, total_invoces

    if triggered_id == 'show-in-progress-btn' and show_in_progress_btn is not None:
        progress_invoces = orders_data.get_in_progress_invoces()
        return orders_db_data, progress_invoces

    if triggered_id == 'show-invoce-content-btn' and shoe_invoce_content_btn is not None:
        content_invoces = orders_data.get_invoce_content(invoces_selRows)
        return content_invoces, invoces_rowdata

    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True, port=8800, host='0.0.0.0')