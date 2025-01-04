from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from oligoMass import molmassOligo as mmo

class orders_tab_manager():

    def __init__(self, tab, price_tab):
        self.df_tab = pd.DataFrame(tab)
        self.price_tab = pd.DataFrame(price_tab)
        self.process_data()

    def process_data(self):
        self.total_price = 0

        df = self.df_tab[self.df_tab['Sequence'] != '']

        len_list = []
        for seq in df['Sequence']:
            len_list.append(mmo.oligoNASequence(seq).size())
        df['Lenght'] = len_list

        self.df_tab.loc[self.df_tab['Sequence'] != '', 'Lenght'] = len_list

        sum_ = df['Lenght'].sum()
        price_ = self.price_tab[self.price_tab['Unit'] == 'simple N']['Price, RUB'].max()

        self.price_tab.loc[self.price_tab['Unit'] == 'simple N', 'Number'] = sum_
        self.price_tab.loc[self.price_tab['Unit'] == 'simple N', 'Sum, RUB'] = sum_ * float(price_)

        lbl_list = list(self.price_tab[self.price_tab['Unit'] != 'simple N']['Unit'])
        for lbl in lbl_list:
            sum_5 = df[df["5'-end"] == lbl].shape[0]
            price_5 = self.price_tab[self.price_tab['Unit'] == lbl]['Price, RUB'].max()

            sum_3 = df[df["3'-end"] == lbl].shape[0]
            price_3 = self.price_tab[self.price_tab['Unit'] == lbl]['Price, RUB'].max()

            sum_purif = df[df["Purification"] == lbl].shape[0]
            price_purif = self.price_tab[self.price_tab['Unit'] == lbl]['Price, RUB'].max()

            if sum_5 > 0:
                self.price_tab.loc[self.price_tab['Unit'] == lbl, 'Number'] = sum_5
                self.price_tab.loc[self.price_tab['Unit'] == lbl, 'Sum, RUB'] = sum_5 * float(price_5)

            if sum_3 > 0:
                self.price_tab.loc[self.price_tab['Unit'] == lbl, 'Number'] = sum_3
                self.price_tab.loc[self.price_tab['Unit'] == lbl, 'Sum, RUB'] = sum_3 * float(price_3)

            if sum_purif > 0:
                self.price_tab.loc[self.price_tab['Unit'] == lbl, 'Number'] = sum_purif
                self.price_tab.loc[self.price_tab['Unit'] == lbl, 'Sum, RUB'] = sum_purif * float(price_purif)

        self.total_price = self.price_tab['Sum, RUB'].sum()


    def get_data(self):
        return self.df_tab.to_dict('records'), self.price_tab.to_dict('records'), self.total_price

    def get_price_tab(self, scale):
        tab = get_price_tab(scale)
        return tab.to_dict('records')


def get_price_tab(scale):

    unit_list = ['simple N', 'BHQ1', 'BHQ2', 'LNA', 'FAM', 'HEX', 'SIMA', 'R6G', 'ROX', 'TAMRA', 'Cy5', 'Cy3', 'HPLC']
    price_1_3_list = [30, 600, 600, 700, 1000, 1500, 1500, 1800, 1000, 1000, 1000, 1000, 1300]
    price_3_10_list = [40, 1000, 1000, 1200, 1800, 2000, 2000, 2200, 1800, 1800, 1800, 1800, 1300]
    price_10_15_list = [45, 1700, 1700, 2300, 2700, 3000, 3000, 3200, 2700, 2700, 2700, 2700, 1300]

    price_df = pd.DataFrame({'Unit': unit_list})
    if scale == '1-3':
        price_df['Price, RUB'] = price_1_3_list
    elif scale == '3-10':
        price_df['Price, RUB'] = price_3_10_list
    else:
        price_df['Price, RUB'] = price_10_15_list

    price_df['Number'] = [0 for i in range(price_df.shape[0])]
    price_df['Sum, RUB'] = [0 for i in range(price_df.shape[0])]

    return price_df

class oligo_orders_form_layout():

    def __init__(self):

        N = 200
        df = pd.DataFrame({'#': [i for i in range(N)],
                           'Name': ['' for i in range(N)],
                           "5'-end": ['' for i in range(N)],
                           'Sequence': ['' for i in range(N)],
                           "3'-end": ['' for i in range(N)],
                           'Amount, o.e.': ['5-10' for i in range(N)],
                           'Purification': ['Cart' for i in range(N)],
                           'Lenght': [0 for i in range(N)]
                           })
        self.tab = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                                        editable=True, id='orders-tab')


        init_scale = '3-10'
        price_df = get_price_tab(init_scale)

        self.price_tab = dash_table.DataTable(price_df.to_dict('records'), [{"name": i, "id": i} for i in price_df.columns],
                                        editable=True, id='price-orders-tab')

        self.layout = html.Div([
            dbc.Row([
                dbc.Col(dbc.Container(self.tab)),
                dbc.Col(dbc.Container(
                    dbc.Row([
                        dbc.Toast(
                            dbc.Button("Update", outline=True, color="secondary",
                                   id='update-orders')),
                        html.Br(),
                        html.Br(),
                        dbc.Toast(
                            dbc.Input(id="total-price", placeholder="", type="text"),
                            header="Calculations:"
                        ),
                        dbc.Toast([
                            dbc.Input(placeholder='Enter invoce number', id='invoce-numbet-text'),
                            html.Br(),
                            dbc.Input(placeholder='Enter client name', id='client-name-text'),
                            html.Br(),
                            dbc.Button("Add to DB", outline=True, color="secondary",
                                       id='add2base-orders')],
                        header='Schedule')
                    ])
                )),
                dbc.Col([
                dbc.Container(html.Div([
                    dcc.Dropdown(['1-3', '3-10', '10-15'], init_scale,
                                 id='synth-scale-selector'),
                    html.Br(),
                    dbc.Container(self.price_tab)
                ]))
                ])
            ])
            ])