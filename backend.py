import os
import requests
import pandas as pd

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
