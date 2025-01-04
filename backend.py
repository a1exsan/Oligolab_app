import os
import requests

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

    def get_orders_by_status_(self, status):
        self.selected_status = status
        url = f'{self.api_db_url}/get_keys_data/{self.db_name}/orders_tab/status/{status}'

        ret = requests.get(url)
        if ret.status_code == 200:
            out = []
            for id, client_id, order_id, input_date, output_date, status, name, sequence, \
                    end5, end3, amount, purification, lenght in ret.json():

                url_ = f'{self.api_db_url}/get_keys_data/{self.db_name}/invoice_tab/id/{order_id}'
                ret_ = requests.get(url_)

                invoce = ret_.json()[0][1]
                client = ret_.json()[0][2]

                d = {}
                d['#'] = id
                d['status'] = status
                d['input date'] = input_date
                d['output date'] = output_date
                d['client id'] = client
                d['order id'] = invoce
                d["5'-end"] = str(end5)
                d["Sequence"] = str(sequence)
                d["3'-end"] = str(end3)
                d['Amount, oe'] = str(amount)
                d['Purification'] = str(purification)
                d['Lenght'] = str(lenght)
                d['Name'] = str(name)
                out.append(d)
            return out
        else:
            return []
