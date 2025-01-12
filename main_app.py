from dash import Dash, Input, Output, Patch, callback, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from flask import request

import backend
import backend_stock

import frontend_layout as frontend

import datetime
from datetime import datetime as ddt

frontend_obj = frontend.oligo_syn_form_layout()
frontend_obj.IP_addres = backend.get_IP_addr()
frontend_obj.make_layout()

orders_data = backend.orders_db(db_IP='127.0.0.1', db_port='8012')
#orders_data = backend.orders_db(db_IP='192.168.17.250', db_port='8012')
#stock_data = backend_stock.stock_manager(db_IP='192.168.17.250', db_port='8012')
stock_data = backend_stock.stock_manager(db_IP='127.0.0.1', db_port='8012')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.title= 'OligosApp'
server = app.server
app.layout = frontend_obj.layout

@callback(
    Output(component_id='orders-tab-database', component_property='rowData', allow_duplicate=True),
    Output(component_id='invoce-tab-database', component_property='rowData', allow_duplicate=True),
    Output(component_id='asm2000-map-tab', component_property='rowData', allow_duplicate=True),

    Input(component_id='pincode-input', component_property='value'),
    Input(component_id='orders-tab-database', component_property='rowData'),
    Input(component_id='orders-tab-database', component_property='selectedRows'),
    Input(component_id='invoce-tab-database', component_property='rowData'),
    Input(component_id='invoce-tab-database', component_property='selectedRows'),
    Input(component_id='asm2000-map-tab', component_property='rowData'),
    Input(component_id='status-order-selector', component_property='value'),
    Input(component_id='show-orders-by-status-btn', component_property='n_clicks'),
    Input(component_id='show-all-invoces-btn', component_property='n_clicks'),
    Input(component_id='show-in-progress-btn', component_property='n_clicks'),
    Input(component_id='show-invoce-content-btn', component_property='n_clicks'),
    Input(component_id='add-sel-order-to-asm2000-btn', component_property='n_clicks'),
    Input(component_id='num-orders-copies-input', component_property='value'),
    Input(component_id='show-not-completed', component_property='n_clicks'),
    Input(component_id='update-outdate-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_orders_db_tab(pincode, orders_db_data, orders_sel_rowdata, invoces_rowdata, invoces_selRows, asm2000_map_rowdata,
                         status_selector, show_by_status_btn,
                         show_all_invoces_btn, show_in_progress_btn, shoe_invoce_content_btn, sel_to_asm_2000_btn,
                         numper_of_copies, show_in_queue_btn, update_orders_tab_btn):

    triggered_id = ctx.triggered_id

    orders_data.pincode = pincode

    if triggered_id == 'show-orders-by-status-btn' and show_by_status_btn is not None:
        orders_tab = orders_data.get_orders_by_status(status_selector)
        return orders_tab, invoces_rowdata, asm2000_map_rowdata

    if triggered_id == 'show-all-invoces-btn' and show_all_invoces_btn is not None:
        total_invoces = orders_data.get_all_invoces()
        return orders_db_data, total_invoces, asm2000_map_rowdata

    if triggered_id == 'show-in-progress-btn' and show_in_progress_btn is not None:
        progress_invoces = orders_data.get_in_progress_invoces()
        return orders_db_data, progress_invoces, asm2000_map_rowdata

    if triggered_id == 'show-invoce-content-btn' and shoe_invoce_content_btn is not None:
        content_invoces = orders_data.get_invoce_content(invoces_selRows)
        return content_invoces, invoces_rowdata, asm2000_map_rowdata

    if triggered_id == 'add-sel-order-to-asm2000-btn' and sel_to_asm_2000_btn is not None:
        asm2000_tab = orders_data.add_selected_order_to_asm2000(numper_of_copies, asm2000_map_rowdata,
                                                                orders_sel_rowdata)
        return orders_db_data, invoces_rowdata, asm2000_tab

    if triggered_id == 'show-not-completed' and show_in_queue_btn is not None:
        orders_tab = orders_data.get_orders_by_status('in queue')
        return orders_tab, invoces_rowdata, asm2000_map_rowdata

    if triggered_id == 'update-outdate-btn' and update_orders_tab_btn is not None:
        orders_data.update_orders_out_date(orders_db_data)
        return orders_db_data, invoces_rowdata, asm2000_map_rowdata

    raise PreventUpdate


@callback(
    Output(component_id='asm2000-map-tab', component_property='rowData', allow_duplicate=True),
    Output(component_id='asm2000-accord-tab', component_property='rowData', allow_duplicate=True),
    Output(component_id='asm2000-map-list-tab', component_property='rowData', allow_duplicate=True),
    Output(component_id='asm2000-map-name', component_property='value', allow_duplicate=True),
    Output(component_id='asm2000-map-synt_number', component_property='value', allow_duplicate=True),

    Input(component_id='pincode-input', component_property='value'),
    Input(component_id='asm2000-map-tab', component_property='rowData'),
    Input(component_id='asm2000-map-tab', component_property='selectedRows'),
    Input(component_id='asm2000-accord-tab', component_property='rowData'),
    Input(component_id='asm2000-map-list-tab', component_property='rowData'),
    Input(component_id='asm2000-map-list-tab', component_property='selectedRows'),
    Input(component_id='asm2000-update-tab-btn', component_property='n_clicks'),
    Input(component_id='asm2000-rename-pos-btn', component_property='n_clicks'),
    Input(component_id='asm2000-change-alk-btn', component_property='n_clicks'),
    Input(component_id='asm2000-gen-map-btn', component_property='n_clicks'),
    Input(component_id='asm2000-update-map', component_property='n_clicks'),
    Input(component_id='asm2000-load-map', component_property='n_clicks'),
    Input(component_id='asm2000-map-name', component_property='value'),
    Input(component_id='asm2000-map-synt_number', component_property='value'),
    Input(component_id='asm2000-start-date-select', component_property='date'),
    Input(component_id='asm2000-save-map-btn', component_property='n_clicks'),
    Input(component_id='asm2000-delete-map', component_property='n_clicks'),
    Input(component_id='asm2000-search-maps-btn', component_property='n_clicks'),
    Input(component_id='asm2000-search-field', component_property='value'),
    Input(component_id='asm2000-print_pass-btn', component_property='n_clicks'),
    Input(component_id='asm2000-update-actual-map', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_asm2000_map(pincode, map_rowdata, sel_map_rowdata, accord_rowdata, map_list_rowdata, sel_map_list_rowdata,
                       update_map_btn, rename_pos_btn, change_alk_btn,
                       gen_map_to_csv_btn, update_maps_btn, load_map_btn,
                       man_name_input, synth_number_input, start_date_select, save_map_btn, delete_map_btn,
                       search_map_btn, search_map_input, print_passport_btn, update_actual_map_btn):

    triggered_id = ctx.triggered_id

    orders_data.pincode = pincode

    if triggered_id == 'asm2000-update-tab-btn' and update_map_btn is not None:
        map_out_tab = orders_data.seq_to_asm_seq(accord_rowdata, map_rowdata)
        accord_out_tab = orders_data.update_accord_tab(accord_rowdata, map_out_tab)
        return map_out_tab, accord_out_tab, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-rename-pos-btn' and rename_pos_btn is not None:
        map_out_tab = orders_data.rename_pos(sel_map_rowdata, map_rowdata)
        return map_out_tab, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-change-alk-btn' and change_alk_btn is not None:
        map_out_tab = orders_data.change_alk(map_rowdata)
        return map_out_tab, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-gen-map-btn' and gen_map_to_csv_btn is not None:
        orders_data.generate_map_to_file('oligo_map.csv',map_rowdata, accord_rowdata)
        return map_rowdata, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-update-map' and update_maps_btn is not None:
        map_list = orders_data.get_oligomaps()
        return map_rowdata, accord_rowdata, map_list, man_name_input, synth_number_input

    if triggered_id == 'asm2000-update-actual-map' and update_actual_map_btn is not None:
        map_list = orders_data.get_actual_maps()
        return map_rowdata, accord_rowdata, map_list, man_name_input, synth_number_input

    if triggered_id == 'asm2000-load-map' and load_map_btn is not None:
        map_out_tab, accord_out_tab, map_name, map_syn_num = orders_data.load_oligomap(sel_map_list_rowdata)
        return map_out_tab, accord_out_tab, map_list_rowdata, map_name, map_syn_num

    if triggered_id == 'asm2000-save-map-btn' and save_map_btn is not None:
        status_code = orders_data.insert_map_to_base(man_name_input, synth_number_input, start_date_select,
                                                     map_rowdata, accord_rowdata)
        #print(f'save map {man_name_input} status code: ', status_code)
        return map_rowdata, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-delete-map' and delete_map_btn is not None:
        status_code = orders_data.delete_map_from_base(sel_map_list_rowdata)
        #print(f'delete map {man_name_input} status code: ', status_code)
        return map_rowdata, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-search-maps-btn' and search_map_btn is not None:
        search_map_list = orders_data.search_maps_by_text(search_map_input)
        if len(search_map_list) > 0:
            return map_rowdata, accord_rowdata, search_map_list, man_name_input, synth_number_input
        else:
            return map_rowdata, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    if triggered_id == 'asm2000-print_pass-btn' and print_passport_btn is not None:
        orders_data.print_pass(map_rowdata, 'map_passport.csv')
        return map_rowdata, accord_rowdata, map_list_rowdata, man_name_input, synth_number_input

    raise PreventUpdate


@callback(
    Output(component_id='asm2000-map-tab', component_property='rowData', allow_duplicate=True),

    Input(component_id='pincode-input', component_property='value'),
    Input(component_id='asm2000-map-tab', component_property='rowData'),
    Input(component_id='asm2000-map-tab', component_property='selectedRows'),
    Input(component_id='asm2000-accord-tab', component_property='rowData'),
    Input(component_id='set-do-lcms-btn', component_property='n_clicks'),
    Input(component_id='set-do-synth-btn', component_property='n_clicks'),
    Input(component_id='set-do-cart-btn', component_property='n_clicks'),
    Input(component_id='set-do-hplc-btn', component_property='n_clicks'),
    Input(component_id='set-do-paag-btn', component_property='n_clicks'),
    Input(component_id='set-do-sed-btn', component_property='n_clicks'),
    Input(component_id='set-do-click-btn', component_property='n_clicks'),
    Input(component_id='set-do-subl-btn', component_property='n_clicks'),
    Input(component_id='set-done-lcms-btn', component_property='n_clicks'),
    Input(component_id='set-done-synth-btn', component_property='n_clicks'),
    Input(component_id='set-done-cart-btn', component_property='n_clicks'),
    Input(component_id='set-done-hplc-btn', component_property='n_clicks'),
    Input(component_id='set-done-paag-btn', component_property='n_clicks'),
    Input(component_id='set-done-sed-btn', component_property='n_clicks'),
    Input(component_id='set-done-click-btn', component_property='n_clicks'),
    Input(component_id='set-done-subl-btn', component_property='n_clicks'),
    Input(component_id='asm2000-update-oligomap-status-btn', component_property='n_clicks'),
    Input(component_id='asm2000-update-order-status-btn', component_property='n_clicks'),
    Input(component_id='asm2000-wasted-status-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_flags_tab(pincode, map_rowdata, sel_map_rowdata, accord_rowdata,
                     do_lcms_btn, do_synth_btn, do_cart_btn, do_hplc_btn, do_paag_btn, do_sed_btn, do_click_btn,
                     do_subl_btn,
                     done_lcms_btn, done_synth_btn, done_cart_btn, done_hplc_btn, done_paag_btn, done_sed_btn,
                     done_click_btn, done_subl_btn, update_omap_status_btn, update_order_status_btn,
                     wasted_sel_btn):
    triggered_id = ctx.triggered_id

    orders_data.pincode = pincode

    if triggered_id == 'set-do-lcms-btn' and do_lcms_btn is not None:
        out_map_data = orders_data.update_map_flags('Do LCMS', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-synth-btn' and do_synth_btn is not None:
        out_map_data = orders_data.update_map_flags('Do synth', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-cart-btn' and do_cart_btn is not None:
        out_map_data = orders_data.update_map_flags('Do cart', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-hplc-btn' and do_hplc_btn is not None:
        out_map_data = orders_data.update_map_flags('Do hplc', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-paag-btn' and do_paag_btn is not None:
        out_map_data = orders_data.update_map_flags('Do paag', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-sed-btn' and do_sed_btn is not None:
        out_map_data = orders_data.update_map_flags('Do sed', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-click-btn' and do_click_btn is not None:
        out_map_data = orders_data.update_map_flags('Do click', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-do-subl-btn' and do_subl_btn is not None:
        out_map_data = orders_data.update_map_flags('Do subl', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-lcms-btn' and done_lcms_btn is not None:
        out_map_data = orders_data.update_map_flags('Done LCMS', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-synth-btn' and done_synth_btn is not None:
        out_map_data = orders_data.update_map_flags('Done synth', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-cart-btn' and done_cart_btn is not None:
        out_map_data = orders_data.update_map_flags('Done cart', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-hplc-btn' and done_hplc_btn is not None:
        out_map_data = orders_data.update_map_flags('Done hplc', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-paag-btn' and done_paag_btn is not None:
        out_map_data = orders_data.update_map_flags('Done paag', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-sed-btn' and done_sed_btn is not None:
        out_map_data = orders_data.update_map_flags('Done sed', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-click-btn' and done_click_btn is not None:
        out_map_data = orders_data.update_map_flags('Done click', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'set-done-subl-btn' and done_subl_btn is not None:
        out_map_data = orders_data.update_map_flags('Done subl', map_rowdata, sel_map_rowdata)
        return out_map_data

    if triggered_id == 'asm2000-update-order-status-btn' and update_order_status_btn is not None:
        orders_data.update_order_status(map_rowdata)
        return map_rowdata

    if triggered_id == 'asm2000-update-oligomap-status-btn' and update_omap_status_btn is not None:
        out_map_data = orders_data.update_oligomap_status(map_rowdata, accord_rowdata)
        return out_map_data

    if triggered_id == 'asm2000-wasted-status-btn' and wasted_sel_btn is not None:
        out_map_data = orders_data.update_map_flags('Wasted', map_rowdata, sel_map_rowdata)
        return out_map_data

    raise PreventUpdate

@callback(
    Output(component_id='asm2000-click-tab', component_property='rowData', allow_duplicate=True),

    Input(component_id='pincode-input', component_property='value'),
    Input(component_id='asm2000-click-tab', component_property='rowData'),
    Input(component_id='asm2000-map-tab', component_property='selectedRows'),
    Input(component_id='asm2000-culc_click-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_click_chem(pincode, click_rowdata, sel_map_rowdata, click_btn):
    triggered_id = ctx.triggered_id

    orders_data.pincode = pincode

    if triggered_id == 'asm2000-culc_click-btn' and click_btn is not None:
        culc_click = orders_data.culc_click(sel_map_rowdata)
        return culc_click

    raise PreventUpdate

@callback(
    Output(component_id='orders-tab', component_property='data', allow_duplicate=True),
    Output(component_id='price-orders-tab', component_property='data', allow_duplicate=True),
    Output(component_id='total-price', component_property='value', allow_duplicate=True),

    Input(component_id='pincode-input', component_property='value'),

    Input(component_id='orders-tab', component_property='data'),
    Input(component_id='price-orders-tab', component_property='data'),
    Input(component_id='total-price', component_property='value'),
    Input(component_id='update-orders', component_property='n_clicks'),

    Input(component_id='add2base-orders', component_property='n_clicks'),
    Input(component_id='invoce-numbet-text', component_property='value'),
    Input(component_id='client-name-text', component_property='value'),
    Input(component_id='synth-scale-selector', component_property='value'),

    prevent_initial_call=True
)
def update_orders_price_tab(pincode, orders_tab, price_tab, total_price_value, update_orders_btn,
                            add_to_base_btn, invoce_input, client_input, select_scale):
    triggered_id = ctx.triggered_id

    orders_data.pincode = pincode

    if triggered_id == 'update-orders' and update_orders_btn is not None:
        out_orders_tab, out_price_tab, total_price = orders_data.compute_price(orders_tab, price_tab)
        return out_orders_tab, out_price_tab, total_price

    if triggered_id == 'add2base-orders' and add_to_base_btn is not None:
        orders_data.add_invoce_to_base(invoce_input, client_input, orders_tab)
        return orders_tab, price_tab, total_price_value

    if triggered_id == 'synth-scale-selector' and select_scale is not None:
        out_price_tab = orders_data.get_price_tab(select_scale)
        return orders_tab, out_price_tab, total_price_value

    raise PreventUpdate


@callback(
    Output(component_id='main-stock-tab-database', component_property='rowData', allow_duplicate=True),
    Output(component_id='output-stock-tab-database', component_property='rowData', allow_duplicate=True),
    Output(component_id='input-stock-tab-database', component_property='rowData', allow_duplicate=True),
    Output(component_id='user-stock-tab-database', component_property='rowData', allow_duplicate=True),

    Input(component_id='pincode-input', component_property='value'),

    Input(component_id='main-stock-tab-database', component_property='rowData'),
    Input(component_id='main-stock-tab-database', component_property='selectedRows'),
    Input(component_id='input-stock-tab-database', component_property='rowData'),
    Input(component_id='output-stock-tab-database', component_property='rowData'),
    Input(component_id='user-stock-tab-database', component_property='rowData'),

    Input(component_id='show-stock-data-btn', component_property='n_clicks'),
    Input(component_id='update-stock-data-btn', component_property='n_clicks'),
    Input(component_id='add-row-stock-data-btn', component_property='n_clicks'),
    Input(component_id='delete-row-stock-data-btn', component_property='n_clicks'),
    Input(component_id='substruct_from-stock-data-btn', component_property='n_clicks'),
    Input(component_id='add-to-stock-data-btn', component_property='n_clicks'),

    prevent_initial_call=True
)
def update_stock_tab(pincode, stock_rowdata, sel_stock_rowdata, input_rowdata, output_rowdata, users_rowdata,
                     show_stock_btn, update_stock_btn, add_row_stock_btn, delete_row_stock_btn,
                     substruct_btn, adjust_btn):
    triggered_id = ctx.triggered_id

    stock_data.pincode = pincode

    if triggered_id == 'show-stock-data-btn' and show_stock_btn is not None:
        out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata = stock_data.show_main_tab_data()
        return out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata

    if triggered_id == 'update-stock-data-btn' and update_stock_btn is not None:
        out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata = (
            stock_data.update_tab(stock_rowdata))
        return out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata

    if triggered_id == 'add-row-stock-data-btn' and add_row_stock_btn is not None:
        out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata = stock_data.add_row()
        return out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata

    if triggered_id == 'delete-row-stock-data-btn' and delete_row_stock_btn is not None:
        out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata = (
            stock_data.delete_rows(sel_stock_rowdata))
        return out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata

    if triggered_id == 'substruct_from-stock-data-btn' and substruct_btn is not None:
        out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata = (
            stock_data.substruct_from_stock('1848570232', 'output_tab', stock_rowdata))
        return out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata

    if triggered_id == 'add-to-stock-data-btn' and substruct_btn is not None:
        out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata = (
            stock_data.substruct_from_stock('1848570232', 'input_tab', stock_rowdata))
        return out_stock_rowdata, out_output_rowdata, out_input_rowdata, out_users_rowdata

    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True, port=8800, host='0.0.0.0')