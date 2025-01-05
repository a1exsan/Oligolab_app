import os
import requests
import pandas as pd
from datetime import datetime
import json
from oligoMass import molmassOligo as mmo
from collections import Counter

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
        self.maps_db_name = 'asm2000_map_1.db'
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


    def seq_to_asm_seq(self, accordRowData, tabRowData):
        tab = pd.DataFrame(tabRowData)
        accord = pd.DataFrame(accordRowData)

        seq_list = []
        for seq in tab['Sequence']:
            oligo = mmo.oligoNASequence(seq)
            df = oligo.getSeqTabDF()
            out_seq = ''
            for mod, nt in zip(df['prefix'], df['nt']):
                if '[' in mod and ']' in mod:
                    m = mod.replace('[', '')
                    m = m.replace(']', '')
                    out_seq += accord[accord['Modification'] == m]['asm2000 position'].max()
                    out_seq += accord[accord['Modification'] == nt]['asm2000 position'].max()
                elif mod == '+' or mod == '*' or mod == 'r' or mod == '':
                    m = f'{mod}{nt}'
                    if nt in 'R M S H V N Y K W B D N'.split(' '):
                        out_seq += nt
                    else:
                        out_seq += accord[accord['Modification'] == m]['asm2000 position'].max()
                else:
                    out_seq += nt

            seq_list.append(out_seq)
        tab['asm Sequence'] = seq_list
        tab['#'] = [i for i in range(1, len(seq_list) + 1)]
        return tab.to_dict('records')

    def get_all_amidites_types(self, seq_list):
        self.amidites_count = Counter()
        for seq in seq_list:
            #print(seq)
            o = mmo.oligoNASequence(seq)
            tab = o.getSeqTabDF()
            for mod, nt in zip(tab['prefix'], tab['nt']):
                if '[' in mod and ']' in mod and mod not in list(self.amidites_count.keys()):
                    self.amidites_count[mod] = 1
                    if nt not in list(self.amidites_count.keys()):
                        self.amidites_count[nt] = 1
                    else:
                        self.amidites_count[nt] += 1
                elif '[' in mod and ']' in mod and mod in list(self.amidites_count.keys()):
                    self.amidites_count[mod] += 1
                    if nt not in list(self.amidites_count.keys()):
                        self.amidites_count[nt] = 1
                    else:
                        self.amidites_count[nt] += 1
                elif mod == '+' or mod == '*' or mod == 'r' or mod == '':
                    a = f'{mod}{nt}'
                    if a not in list(self.amidites_count.keys()):
                        self.amidites_count[a] = 1
                    else:
                        self.amidites_count[a] += 1

    def update_accord_tab(self, accordRowData, tabRowData):
        tab = pd.DataFrame(tabRowData)
        accord = pd.DataFrame(accordRowData)

        round_n = 3
        constant_vol = 0.10

        self.get_all_amidites_types(list(tab['Sequence']))
        for mod, count in zip(self.amidites_count.keys(), self.amidites_count.values()):
            #print(mod, count)
            if '[' in mod and ']' in mod:
                m = mod.replace('[', '')
                m = m.replace(']', '')
                r5 = accord[accord['Modification'] == m]['ul on step, 5mg'].max()
                r10 = accord[accord['Modification'] == m]['ul on step, 10mg'].max()
                conc = accord[accord['Modification'] == m]['Conc, g/ml'].max()

                vol5 = r5 * count / 1000
                vol10 = r10 * count / 1000

                vol5 += vol5 * constant_vol
                vol10 += vol10 * constant_vol

                if vol5 <= 1.5:
                    vol5 = 1.5
                if vol10 <= 1.5:
                    vol10 = 1.5

                accord.loc[accord['Modification'] == m, 'Amount 5mg, ml'] = round(vol5, round_n)
                accord.loc[accord['Modification'] == m, 'Amount 10mg, ml'] = round(vol10, round_n)
                accord.loc[accord['Modification'] == m, 'Amount 5mg, g'] = round(conc * vol5, round_n)
                accord.loc[accord['Modification'] == m, 'Amount 10mg, g'] = round(conc * vol10, round_n)
            else:

                r5 = accord[accord['Modification'] == mod]['ul on step, 5mg'].max()
                r10 = accord[accord['Modification'] == mod]['ul on step, 10mg'].max()
                conc = accord[accord['Modification'] == mod]['Conc, g/ml'].max()

                vol5 = r5 * count / 1000
                vol10 = r10 * count / 1000

                vol5 += vol5 * constant_vol
                vol10 += vol10 * constant_vol

                if vol5 <= 1.5:
                    vol5 = 1.5
                if vol10 <= 1.5:
                    vol10 = 1.5

                accord.loc[accord['Modification'] == mod, 'Amount 5mg, ml'] = round(vol5, round_n)
                accord.loc[accord['Modification'] == mod, 'Amount 10mg, ml'] = round(vol10, round_n)
                accord.loc[accord['Modification'] == mod, 'Amount 5mg, g'] = round(conc * vol5, round_n)
                accord.loc[accord['Modification'] == mod, 'Amount 10mg, g'] = round(conc * vol10, round_n)

        return accord.to_dict('records')

    def get_pos_list(self, start):
        pos_list = []
        for j in range(1, 13):
            for i in 'A B C D E F G H'.split(' '):
                pos_list.append(f'{i}{j}')
        return pos_list[pos_list.index(start):]

    def rename_pos(self, selrowData, rowData):
        first = selrowData[0]
        selDF = pd.DataFrame(selrowData)
        DF = pd.DataFrame(rowData)

        synth_number = first['Synt number']
        name = first['Position']
        pos_list = self.get_pos_list(name)

        selDF['Position'] = pos_list[: selDF.shape[0]]

        for _, pos in zip(selDF['#'], selDF['Position']):
            DF.loc[DF['#'] == _, 'Position'] = pos
            DF.loc[DF['#'] == _, 'Synt number'] = synth_number

        return DF.to_dict('records')

    def change_alk(self, rowData):
        out = []
        for row in rowData:
            oligo = mmo.oligoNASequence(row['Sequence'])
            tab = oligo.getSeqTabDF()
            #print(oligo.sequence)
            r = row.copy()
            if ((str(tab['prefix'].loc[1]).find('FAM') == -1) and (str(tab['prefix'].loc[1]) != '') and
                    (str(tab['prefix'].loc[1]).find('Alk') == -1)):
                #sseq = [f'{i}{j}']
                #seq = f"[Alk]{''.join(list(tab['nt']))}{str(tab['suffix'].loc[tab.shape[0]])}"
                sseq = row['Sequence']
                seq = sseq.replace(sseq[sseq.find('[') + 1: sseq.find(']')], 'Alk')
                pref = str(tab['prefix'].loc[1])
                pref = pref.replace('[', '')
                pref = pref.replace(']', '')
                purif_type = row['Purif type'] + f"_{pref}"
                r['Sequence'] = seq
                r['Purif type'] = purif_type
            out.append(r)

        return out

    def generate_map_to_file(self, filename, rowData, accordData):
        data = pd.DataFrame(rowData)
        accord = pd.DataFrame(accordData)
        self.filename = f'{filename}.xlsx'
        self.writer = pd.ExcelWriter(self.filename, engine='openpyxl')
        data.to_excel(self.writer, sheet_name='main', startrow = 0, index=False, header=True)
        accord.to_excel(self.writer, sheet_name='main', startrow = data.shape[0] + 2, index=False, header=True)
        self.writer._save()


    def map_in_progress(self, mapdata):
        map = json.loads(mapdata)
        df = pd.DataFrame(map)
        try:
            return round(df[df['Status'] == 'finished'].shape[0] * 100/df.shape[0], 0)
        except:
            return 100

    def get_oligomaps(self):
        url = f'{self.api_db_url}/get_all_tab_data/{self.maps_db_name}/main_map'
        ret = requests.get(url)
        if ret.status_code == 200:
            out = []
            for r in ret.json():
                d = {}
                d['#'] = r[0]
                d['Map name'] = r[2]
                d['Synth number'] = r[3]
                d['Date'] = r[1]
                d['in progress'] = self.map_in_progress(r[4])
                out.append(d)
            return out
        else:
            return []

    def load_oligomap(self, seldata):
        if len(seldata) > 0:
            url = f"{self.api_db_url}/get_keys_data/{self.maps_db_name}/main_map/id/{seldata[0]['#']}"
            ret = requests.get(url)
            if ret.status_code == 200:
                self.oligo_map_id = seldata[0]['#']
                meta = ret.json()
                map_data = json.loads(meta[0][4])
                accord_data = json.loads(meta[0][5])
                #print(meta)
                return map_data, accord_data, meta[0][2], meta[0][3]
            else:
                self.oligo_map_id = -1
                return [], []

    def insert_map_to_base(self, name, synth_number, synth_date, rowData, accordData):
        if len(rowData) > 0:
            url = f"{self.api_db_url}/insert_data/{self.maps_db_name}/main_map"
            r = requests.post(url,
                              json=json.dumps([synth_date, name, synth_number,
                                               json.dumps(rowData),
                                               json.dumps(accordData)]))
            return r.status_code
        else:
            return 404

    def delete_map_from_base(self, seldata):
        if len(seldata) > 0:
            self.oligo_map_id = -1
            url = f"{self.api_db_url}/delete_data/{self.maps_db_name}/main_map/{seldata[0]['#']}"
            ret = requests.delete(url)
            return ret.status_code
        else:
            return 404