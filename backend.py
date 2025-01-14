import os
import requests
import pandas as pd
from datetime import datetime
import json
from oligoMass import molmassOligo as mmo
from collections import Counter
import price_data

class click_azide():

    def __init__(self, oligos_sequence, amount_oe):
        self.seq = oligos_sequence
        self.amount = amount_oe
        self.tab = {}
        self.__rools_protocol()

    def __react_volume(self):
        o = mmo.oligoNASequence(self.seq)
        self.amount_nmol = self.amount * 1e6 / o.getExtinction()
        self.tab['amount nmol'] = round(self.amount_nmol, 2)
        self.tab['sequence'] = self.seq
        self.tab['amount oe'] = round(self.amount, 2)
        if self.amount_nmol >= 1 and self.amount_nmol <= 20:
            return 100
        elif self.amount_nmol > 20 and self.amount_nmol <= 40:
            return 200
        elif self.amount_nmol > 40 and self.amount_nmol <= 80:
            return 400
        elif self.amount_nmol > 80 and self.amount_nmol <= 600:
            return 600
        else:
            return 700

    def __rools_protocol(self):
        react_volume = self.__react_volume()
        self.tab['react volume, ul'] = react_volume
        self.tab['azide volume, ul'] = round(self.amount_nmol * 0.15, 0)
        self.tab['Cu buffer volume, ul'] = round(react_volume * 0.67, 0)
        self.tab['activator volume, ul'] = round(react_volume * 0.02, 0)
        self.tab['water volume, ul'] = round(react_volume - self.tab['azide volume, ul'] -
                                        self.tab['Cu buffer volume, ul'] - self.tab['activator volume, ul'], 0)

    def __call__(self, *args, **kwargs):
        return self.tab

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
        self.pincode = ''

    def headers(self):
        return {'Authorization': f'Pincode {self.pincode}'}

class orders_db(api_db_interface):
    def __init__(self, db_IP, db_port):
        super().__init__(db_IP, db_port)

        self.db_name = 'scheduler_oligolab_2.db'
        self.maps_db_name = 'asm2000_map_1.db'
        self.selected_status = 'finished'
        self.strftime_format = "%Y-%m-%d"
        self.oligo_map_id = -1

    def get_orders_by_status(self, status):
        self.selected_status = status
        url = f'{self.api_db_url}/get_orders_by_status/{self.db_name}/{status}'
        ret = requests.get(url, headers=self.headers())
        return ret.json()

    def get_all_invoces(self):
        url = f'{self.api_db_url}/get_all_invoces/{self.db_name}'
        ret = requests.get(url, headers=self.headers())
        return ret.json()

    def check_pincode(self):
        url = f'{self.api_db_url}/get_all_invoces/{self.db_name}'
        ret = requests.get(url, headers=self.headers())
        return ret.status_code == 200

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
            orders_list = requests.get(url, headers=self.headers())
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
            'Support type': ['biocomma_1000' for i in range(1, len(names_list) + 1)],
            'Date': [datetime.now().date().strftime(self.strftime_format) for i in range(len(names_list))],
            'Synt number': list([1 for i in range(1, len(names_list) + 1)]),
            'Position': pos_list,
            'CPG, mg': cpg_list,
            'Scale, OE': amount_list,
            'asm Sequence': seq_list,
            'Status': ['in queue' for i in range(1, len(names_list) + 1)],
            'Dens, oe/ml': [0. for i in range(1, len(names_list) + 1)],
            'Vol, ml': [0.3 for i in range(1, len(names_list) + 1)],
            'Purity, %': [50. for i in range(1, len(names_list) + 1)],

            'Do LCMS': [False for i in range(1, len(names_list) + 1)],
            'Do synth': [False for i in range(1, len(names_list) + 1)],
            'Do cart': [False for i in range(1, len(names_list) + 1)],
            'Do hplc': [False for i in range(1, len(names_list) + 1)],
            'Do paag': [False for i in range(1, len(names_list) + 1)],
            'Do sed': [False for i in range(1, len(names_list) + 1)],
            'Do click': [False for i in range(1, len(names_list) + 1)],
            'Do subl': [False for i in range(1, len(names_list) + 1)],
            'Done LCMS': [False for i in range(1, len(names_list) + 1)],
            'Done synth': [False for i in range(1, len(names_list) + 1)],
            'Done cart': [False for i in range(1, len(names_list) + 1)],
            'Done hplc': [False for i in range(1, len(names_list) + 1)],
            'Done paag': [False for i in range(1, len(names_list) + 1)],
            'Done sed': [False for i in range(1, len(names_list) + 1)],
            'Done click': [False for i in range(1, len(names_list) + 1)],
            'Done subl': [False for i in range(1, len(names_list) + 1)],
            'DONE': [False for i in range(1, len(names_list) + 1)],
            'Wasted': [False for i in range(1, len(names_list) + 1)]
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
                                                            sequence, end5, end3, amount, purification]}),
                            headers=self.headers())
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
        ret = requests.get(url, headers=self.headers())

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

    def get_actual_maps(self):
        total_maps = self.get_oligomaps_data()
        if len(total_maps) > 0:
            out = []
            for row in total_maps:
                df = row['map data']
                if df.shape[0] > 0:
                    if df[(df['DONE'] == True)|(df['Wasted'] == True)].shape[0] != df.shape[0]:
                        d = {}
                        d['#'] = row['#']
                        d['Map name'] = row['Map name']
                        d['Synth number'] = row['Synth number']
                        d['Date'] = row['Date']
                        d['in progress'] = row['in progress']
                        out.append(d)
            return out
        else:
            return []

    def get_oligomaps_data(self):
        url = f'{self.api_db_url}/get_all_tab_data/{self.maps_db_name}/main_map'
        ret = requests.get(url, headers=self.headers())
        if ret.status_code == 200:
            out = []
            for r in ret.json():
                d = {}
                d['#'] = r[0]
                d['Map name'] = r[2]
                d['Synth number'] = r[3]
                d['Date'] = r[1]
                d['in progress'] = self.map_in_progress(r[4])
                d['map data'] = pd.DataFrame(json.loads(r[4]))
                out.append(d)
            return out
        else:
            return []

    def load_oligomap(self, seldata):
        if len(seldata) > 0:
            url = f"{self.api_db_url}/get_keys_data/{self.maps_db_name}/main_map/id/{seldata[0]['#']}"
            ret = requests.get(url, headers=self.headers())
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
                                               json.dumps(accordData)]), headers=self.headers())
            return r.status_code
        else:
            return 404

    def delete_map_from_base(self, seldata):
        if len(seldata) > 0:
            self.oligo_map_id = -1
            url = f"{self.api_db_url}/delete_data/{self.maps_db_name}/main_map/{seldata[0]['#']}"
            ret = requests.delete(url, headers=self.headers())
            return ret.status_code
        else:
            return 404

    def search_maps_by_text(self, text):
        db_content = self.get_oligomaps_data()
        out = []
        for row in db_content:
            df = row['map data']

            if 'Sequence' in list(df.keys()):
                df_seq = df[df['Sequence'] == text]
            if 'Name' in list(df.keys()):
                df_name = df[df['Name'] == text]
            try:
                if 'Order id' in list(df.keys()):
                    df_id = df[df['Order id'] == int(text)]
            except:
                df_id = pd.DataFrame()

            if (df_seq.shape[0] > 0) or (df_name.shape[0] > 0) or (df_id.shape[0] > 0):

                d = {}
                d['#'] = row['#']
                d['Map name'] = row['Map name']
                d['Synth number'] = row['Synth number']
                d['Date'] = row['Date']
                d['in progress'] = row['in progress']
                out.append(d)

        return out

    def  print_pass(self, rowData, filename):
        out_tab = []
        for row in rowData:
            o = mmo.oligoNASequence(row['Sequence'])
            d = {}
            d['Position'] = row['Position']
            d['Name'] = row['Name'] + f"  ({row['Position']})"
            d['Sequence'] = row['Sequence']
            d['Amount, oe'] = int(round(row['Dens, oe/ml'] * row['Vol, ml'], 0))
            if o.getExtinction() > 0:
                d['Amount, nmol'] = int(round(d['Amount, oe'] * 1e6 / o.getExtinction(), 0))
            else:
                d['Amount, nmol'] = 0.
            d['Desolving'] = int(d['Amount, nmol'] * 10)

            d['Purification'] = row['Purif type']
            d['order ID'] = row['Order id']
            d['Mass, Da'] = round(o.getAvgMass(), 2)
            d['Extinction'] = o.getExtinction()

            out_tab.append(d)
        df = pd.DataFrame(out_tab)
        df.to_csv(filename, sep=';')

    def download_sequences_file(self, rowData):
        seq_file = ''
        for row in rowData:
            seq_file += f"{row['Position']},{row['asm Sequence']},+\n"
        return seq_file


    def update_map_flags(self, type_flags, rowData, selrowData):

        if len(selrowData) == 0:
            index_list = list(pd.DataFrame(rowData)['#'])
        else:
            index_list = list(pd.DataFrame(selrowData)['#'])

        out = []
        for row in rowData:
                d = row.copy()
                if row['#'] in index_list:
                    if type_flags in list(row.keys()):
                        d[type_flags] = not d[type_flags]
                    else:
                        d[type_flags] = True
                out.append(d)
        return out

    def get_order_status(self, row):
        state_list = ['synth', 'sed', 'click', 'cart', 'hplc', 'paag', 'LCMS', 'subl']
        flag_list = []
        for state in state_list:
            flag_list.append(row[f'Do {state}'] == row[f'Done {state}'])
        status = 'synthesis'
        for i in range(8):
            if not flag_list[i]:
                if i < 3:
                    status = 'synthesis'
                elif i > 2 and i < 6:
                    status = 'purification'
                elif i == 7:
                    status = 'formulation'
                return status
            else:
                if i == 7:
                    status = 'finished'
                    return status
        return status


    def update_oligomap_status(self, rowData, accordrowdata):
        if self.oligo_map_id > -1:
            out = []
            for row in rowData:
                out.append(row)
                out[-1]['Status'] = self.get_order_status(row)
                if out[-1]['Status'] == 'finished':
                    out[-1]['DONE'] = True
                else:
                    out[-1]['DONE'] = False

            url = f"{self.api_db_url}/update_data/{self.maps_db_name}/main_map/{self.oligo_map_id}"
            r = requests.put(url,
                              json=json.dumps({
                                  'name_list': ['map_tab', 'accord_tab'],
                                  'value_list': [
                                      json.dumps(out),
                                      json.dumps(accordrowdata)
                                  ]
                              })
                             , headers=self.headers())
            print(f'update status {self.oligo_map_id}: {r.status_code}')
            return out
        else:
            return rowData

    def update_order_status(self, rowData):
        if len(rowData) > 0:
            for row in rowData:
                order_id = row['Order id']
                order_date = row['Date']
                order_status = row['Status']

                url = f"{self.api_db_url}/update_data/{self.db_name}/orders_tab/{order_id}"
                r = requests.put(url,
                    json=json.dumps({
                        'name_list': ['output_date', 'status'],
                        'value_list': [order_date, order_status]
                    })
                , headers=self.headers())

    def culc_click(self, selrowdata):
        out = []
        for row in selrowdata:
            seq = row['Sequence']
            amount = row['Dens, oe/ml'] * row['Vol, ml']
            d = click_azide(seq, amount)()
            d['Order id'] = row['Order id']
            d['Position'] = row['Position']
            d['Dye'] = row['Purif type']
            out.append(d)
        return out

    def compute_price(self, tab, price_tab):
        self.df_tab = pd.DataFrame(tab)
        self.price_tab = pd.DataFrame(price_tab)

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
        return self.df_tab.to_dict('records'), self.price_tab.to_dict('records'), self.total_price

    def add_invoce_to_base(self, invoce, client, data):
        url = f"{self.api_db_url}/insert_data/{self.db_name}/invoice_tab"
        r = requests.post(url, json=json.dumps([invoce, client]), headers=self.headers())

        url = f"{self.api_db_url}/get_all_tab_data/{self.db_name}/invoice_tab"
        r = requests.get(url, headers=self.headers())
        id_list = [row[0] for row in r.json()]
        invoce_id = max(id_list)

        out_dataframe = pd.DataFrame(data)
        out_dataframe = out_dataframe[out_dataframe['Sequence'] != '']

        out_dataframe['order id'] = invoce_id
        out_dataframe['client id'] = invoce_id
        out_dataframe['input date'] = datetime.now().strftime('%m.%d.%Y')
        out_dataframe['output date'] = datetime.now().strftime('%m.%d.%Y')
        out_dataframe['status'] = 'in queue'
        out_dataframe['Sequence'] = out_dataframe['Sequence'].str.upper()
        out_dataframe.loc[out_dataframe["5'-end"] == '', "5'-end"] = 'none'
        out_dataframe.loc[out_dataframe["3'-end"] == '', "3'-end"] = 'none'

        len_list = []
        for seq in out_dataframe['Sequence']:
            len_list.append(mmo.oligoNASequence(seq).size())

        out_dataframe['lenght'] = len_list

        for (client_id, order_id, input_date, output_date, status,
             sequence, end5, end3, amount, purification, lenght, name) in zip(
            out_dataframe['client id'],
            out_dataframe['order id'],
            out_dataframe['input date'],
            out_dataframe['output date'],
            out_dataframe['status'],
            out_dataframe['Sequence'],
            out_dataframe["5'-end"],
            out_dataframe["3'-end"],
            out_dataframe['Amount, o.e.'],
            out_dataframe['Purification'],
            out_dataframe['lenght'],
            out_dataframe['Name'],
        ):
            url = f"{self.api_db_url}/insert_data/{self.db_name}/orders_tab"
            r = requests.post(url, json=json.dumps([client_id, order_id, input_date, output_date,
                               status, name, sequence, end5, end3, amount, purification, lenght]),
                              headers=self.headers())

    def get_price_tab(self, scale):
        tab = price_data.get_price_tab(scale)
        return tab.to_dict('records')



def test1():
    orders_data = orders_db(db_IP='127.0.0.1', db_port='8012')
    rowdata = orders_data.get_oligomaps_data()

    for row in rowdata:
        map_id = row['#']
        df = row['map data']
        if 'Status' not in list(df.keys()):
            df['Status'] = ['finished' for i in range(df.shape[0])]

        df['DONE'] = [False for i in range(df.shape[0])]
        df['Wasted'] = [False for i in range(df.shape[0])]
        df.loc[df['Status'] == 'finished', 'DONE'] = True
        df.loc[df['Status'] != 'finished', 'Wasted'] = True

        url = f"{orders_data.api_db_url}/update_data/{orders_data.maps_db_name}/main_map/{map_id}"
        r = requests.put(url,
                         json=json.dumps({
                             'name_list': ['map_tab'],
                             'value_list': [
                                 json.dumps(df.to_dict('records'))
                             ]
                         })
                         , headers={'Authorization': f'Pincode {orders_data.pincode}'})




if __name__ == '__main__':
    #test1()
    pass