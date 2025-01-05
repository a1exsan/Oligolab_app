import os
import requests
import pandas as pd
from datetime import datetime
import json

def get_IP_addr():
    ipdata = os.popen('ip -br a').read()
    ipdata = ipdata.split('\n')
    out = ''
    for i in ipdata:
        if i.find('wlp') > -1:
            out = i
            break
    IP = out[out.find('UP')+2:out.find('/')]
    return out, IP

class api_db_interface():

    def __init__(self, db_IP, db_port):
        self.db_IP = db_IP
        self.db_port = db_port
        self.api_db_url = f'http://{self.db_IP}:{self.db_port}'

class orders_db(api_db_interface):
    def __init__(self, db_IP, db_port):
        super().__init__(db_IP, db_port)

        self.db_name = 'scheduler_oligolab_2.db'
        self.selected_status = 'finished'
        self.strftime_format = "%Y-%m-%d"

    def get_orders_by_status(self, status):
        self.selected_status = status
        url = f'{self.api_db_url}/get_orders_by_status/{self.db_name}/{status}'
        ret = requests.get(url)
        return ret.json()

    def get_all_invoces(self):
        url = f'{self.api_db_url}/get_all_invoces/{self.db_name}'
        ret = requests.get(url)
        return ret.json()

    def get_in_progress_invoces(self):
        data = self.get_all_invoces()
        out = []
        for row in data:
            if row['status'] == 'in progress':
                out.append(row)
        return out

    def get_invoce_content(self, selRows):
        out = pd.DataFrame(
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
        out = out.to_dict('records')
        for row in selRows:
            out = []
            url = f"{self.api_db_url}/get_keys_data/{self.db_name}/orders_tab/order_id/{row['#']}"
            #orders_list = self.uny_db.get_all_tab_data_by_keys('orders_tab', 'order_id', row['#'])
            orders_list = requests.get(url)
            for r in orders_list.json():
                d = {}
                d['#'] = r[0]
                d['status'] = r[5]
                d['input date'] = r[3]
                d['output date'] = r[4]
                d['client id'] = row['client']
                d['order id'] = row['invoce']
                d["5'-end"] = str(r[8])
                d["Sequence"] = str(r[7])
                d["3'-end"] = str(r[9])
                d['Amount, oe'] = str(r[10])
                d['Purification'] = str(r[11])
                d['Lenght'] = str(r[12])
                d['Name'] = str(r[6])
                out.append(d)
            break
        return out

    def get_suport_amount(self, amount):
        if amount in ['1-3', '1-5', '3-5']:
            return '5'
        elif amount == '5-10':
            return '5'
        elif amount in ['10-15', '15-20', '10-20']:
            return '10'
        else:
            return '10'

    def add_selected_order_to_asm2000(self, copies_number, rowData, selRowData):

        seq_list, names_list, amount_list, cpg_list, pos_list, order_id_list, purif_type \
            = [], [], [], [], [], [], []

        out_sel = []
        if copies_number not in [None, '']:
            for row in selRowData:
                out_sel.extend([row for i in range(int(copies_number))])
        else:
            out_sel.extend(row for row in selRowData)

        for row in out_sel:
            seq_id = row['#']
            end5 = row["5'-end"]
            end3 = row["3'-end"]
            sequence = row['Sequence']
            name = row['Name']
            amount = row['Amount, oe']

            order_id_list.append(seq_id)
            purif_type.append(row['Purification'])

            s = sequence
            if end5.lower() != 'none':
                s = f'[{end5}]{s}'
            if end3.lower() != 'none':
                s = f'{s}[{end3}]'
            seq_list.append(s)

            names_list.append(name)
            cpg_list.append(self.get_suport_amount(amount))
            amount_list.append(amount)

            pos_list.append('A1')

        out_tab = {
            '#': [i for i in range(1, len(names_list) + 1)],
            'Order id': order_id_list,
            'Name': names_list,
            'Sequence': seq_list,
            'Purif type': purif_type,
            'Date': [datetime.now().date().strftime(self.strftime_format) for i in range(len(names_list))],
            'Synt number': list([1 for i in range(1, len(names_list) + 1)]),
            'Position': pos_list,
            'CPG, mg': cpg_list,
            'Scale, OE': amount_list,
            'asm Sequence': seq_list,
            'Status': ['in queue' for i in range(1, len(names_list) + 1)],
            'Dens, oe/ml': [0. for i in range(1, len(names_list) + 1)],
            'Vol, ml': [0.3 for i in range(1, len(names_list) + 1)],
            'Purity, %': [50. for i in range(1, len(names_list) + 1)]
        }

        #print(out_tab)

        df = pd.DataFrame(rowData)
        df_sel = pd.DataFrame(out_tab)
        if df.shape[0] > 1:
            df = pd.concat([df, df_sel])
        else:
            df = pd.DataFrame(out_tab)

        return df.to_dict('records')

    def update_orders_out_date(self, rowData):
        for row in rowData:
            id = row['#']
            status = row['status']
            input_date = row['input date']
            output_date = row['output date']
            name = row['Name']
            end5 = row["5'-end"]
            end3 = row["3'-end"]
            sequence = row["Sequence"]
            amount = row['Amount, oe']
            purification = row['Purification']

            url = f"{self.api_db_url}/update_data/{self.db_name}/orders_tab/{id}"
            r = requests.put(url,
                             json=json.dumps({'name_list':['input_date', 'output_date', 'status', 'name',
                                                           'sequence', 'end5', 'end3', 'amount', 'purification'],
                                              'value_list':[input_date, output_date, status, name,
                                                            sequence, end5, end3, amount, purification]}))
            #print(id, name, sequence, r.status_code)
            #self.db.update_orders_tab(id, input_date, output_date, status, name,
            #                          sequence, end5, end3, amount, purification)