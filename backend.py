import os
import requests
import pandas as pd
from datetime import datetime
import json
from oligoMass import molmassOligo as mmo
from collections import Counter
import price_data
from datetime import datetime
from datetime import timedelta

class support_base():
    def __init__(self):
        self.support_capasity = {}
        self.support_capasity['biocomma_500'] = 85.
        self.support_capasity['biocomma_1000'] = 42.
        self.support_capasity['biocomma_2000'] = 39.
        self.support_capasity['bhq1_1000_hg'] = 45.
        self.support_capasity['bhq2_1000_hg'] = 45.
        self.support_capasity['bhq3_500'] = 50.
        self.support_capasity['bhq1_1000'] = 45.
        self.support_capasity['bhq1_500'] = 50.
        self.support_capasity['bhq2_500'] = 50.
        self.support_capasity['bhq2_1000'] = 45.
        self.support_capasity['PO3_500'] = 50.

        self.scale_intervals = {}
        self.scale_intervals['1 mg'] = (2, 3)
        self.scale_intervals['3 mg'] = (3, 5)
        self.scale_intervals['5 mg'] = (5, 8)


class oligo_amount_model():
    def __init__(self, seq, syn_yield):
        self.oligo = mmo.oligoNASequence(seq)
        self.syn_yield = syn_yield
        self.base_yield = 0.2
        self.purif_yield = 0.7

    def read_amount(self, amount):
        if amount.find('-') > -1:
            self.low_limit = float(amount[:amount.find('-')])
            self.hi_limit = float(amount[amount.find('-')+1:])
        else:
            self.low_limit, self.hi_limit = float(amount)

    def get_cpg_mg(self, amount, capacity, cart=True, hplc=False):
        self.read_amount(amount)
        oe = (self.low_limit + self.hi_limit) / 2
        ext = self.oligo.getExtinction()
        if ext > 0:
            nmol = oe * 1e6 / self.oligo.getExtinction()
        else:
            nmol = 10.
        cpg_mg = nmol / (self.oligo_len_correction() * capacity)
        if hplc:
            cpg_mg /= self.purif_yield
        return cpg_mg

    def oligo_len_correction(self):
        x = [self.syn_yield, 0.05]
        y = [20, 100]
        self.k = (x[1] - x[0]) / (y[1] - y[0])
        self.b = x[1] - self.k * y[1]
        return self.oligo.size() * self.k + self.b



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
        self.solutions_db_name = 'solutions_oligolab_1.db'
        self.hist_db_name = 'request_history_1.db'
        self.hist_data_db_name = 'oligomap_history_2.db'
        self.stock_db_name = 'stock_oligolab_5.db'
        self.selected_status = 'finished'
        self.strftime_format = "%Y-%m-%d"
        self.oligo_map_id = -1
        self.all_not_fin_oligos = []

    def get_orders_by_status(self, status):

        def get_in_progress():
            out = []
            for st in ['synthesis', 'purification', 'formulation']:
                url = f'{self.api_db_url}/get_orders_by_status/{self.db_name}/{st}'
                ret = requests.get(url, headers=self.headers())
                out.extend(ret.json())
            return out

        self.selected_status = status
        out = []
        if status == 'in progress':
            out = get_in_progress()
        elif status == 'wasted-in progress':
            inprogress = get_in_progress()
            self.get_oligomaps()
            df = pd.DataFrame(self.all_not_fin_oligos)
            for row in inprogress:
                c_df = df[df['Order id'] == row['#']]
                if c_df[c_df['map #'] == c_df['map #'].max()]['Wasted'].max() == True:
                    out.append(row)
        else:
            url = f'{self.api_db_url}/get_orders_by_status/{self.db_name}/{status}'
            ret = requests.get(url, headers=self.headers())
            out.extend(ret.json())
        return out

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
            if row['status'] == 'in progress' or not row['send']:
                out.append(row)
        out = self.set_invoces_timing_prognosis(out)
        return out

    def  get_oligo_prep_prognosis(self, d, cc = 1):
        data = self.get_invoce_content([d])
        df = pd.DataFrame(data)
        fam_count = df[df["5'-end"].str.contains('FAM')].shape[0]
        primer_count = df[df["5'-end"] == 'none'].shape[0]
        alk_count = df.shape[0] - fam_count - primer_count
        if primer_count == df.shape[0]:
            return 3 + cc
        elif primer_count <  df.shape[0] and alk_count == 0:
            return 5 + cc
        elif primer_count <  df.shape[0] and alk_count > 0:
            return 7 + cc

    def set_invoces_timing_prognosis(self, tab):
        out = []
        for row in tab:
            d = row.copy()
            n_days = self.get_oligo_prep_prognosis(d, cc=2)
            out_date = datetime.strptime(d['input date'], '%m.%d.%Y') + timedelta(days=n_days)

            start_date = datetime.strptime(d['input date'], '%m.%d.%Y')
            now_date = datetime.now()
            delta_days = (out_date - now_date).days
            prod_days = (now_date - start_date).days

            #if delta_days > 0:
            d['out date'] = out_date.strftime('%d.%m.%Y')

            if delta_days > 0:
                d['days_left'] = str(delta_days)
            elif delta_days == 0:
                d['days_left'] = '0+'
            else:
                d['days_left'] = '0'
            d['product days'] = f"{prod_days}/{n_days}"
            out.append(d)
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
        if amount in ['1-3', '1-5', '3-5', '5-10', '3-10']:
            return '3'
        elif amount in ['10-15']:
            return '5'
        elif amount in ['15-20', '10-20']:
            return '8'
        else:
            return '10'

    def get_support_type(self, sequence):
        oligo = mmo.oligoNASequence(sequence)
        if sequence.find('BHQ1') > -1:
            return 'bhq1_1000_hg'
        elif sequence.find('BHQ2') > -1:
            return 'bhq2_1000_hg'
        elif sequence.find('BHQ3') > -1:
            return 'bhq3_500'

        if oligo.size() <= 30:
            return 'biocomma_500'
        elif oligo.size() > 30 and oligo.size() <= 65:
            return 'biocomma_1000'
        elif oligo.size() > 65 and oligo.size() <= 110:
            return 'biocomma_2000'
        elif oligo.size() > 110 and oligo.size() <= 500:
            return 'biocomma_3000'
        else:
            return 'biocomma_3000'

    def get_purif_click_type(self, sequence):
        if sequence.find('FAM]') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': False}
        elif sequence.find('[HEX') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        elif sequence.find('[R6G') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        elif sequence.find('[SIMA') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        elif sequence.find('[ROX') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        elif sequence.find('[Cy') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        elif sequence.find('[TAMR') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        elif sequence.find('[Alk') > -1:
            return {'cart': False, 'hplc': True, 'lcms': True, 'click': True}
        else:
            return {'cart': True, 'hplc': False, 'lcms': False, 'click': False}


    def add_selected_ords_to_asm2000_cpg(self, rowData, selRowData, scale_type='1 mg', syn_yield=0.2):
        out_first = self.add_selected_order_to_asm2000(1, [], selRowData)
        support = support_base()
        if len(rowData) == 1:
            if rowData[0]['#'] == 0:
                rowData = []
        if len(rowData) > 0:
            out = rowData.copy()
        else:
            out = []
        for row in out_first:
            d = row.copy()
            cpg_model = oligo_amount_model(row['Sequence'], syn_yield)
            cpg_mg = cpg_model.get_cpg_mg(row['Scale, OE'], support.support_capasity[row['Support type']],
                                          hplc=row['Do hplc'] or row['Do paag'])
            c = cpg_mg / support.scale_intervals[scale_type][0]
            count = 1
            if c > 1:
                count = int(round(c, 0))
            for i in range(count):
                d['CPG, mg'] = support.scale_intervals[scale_type][1]
                out.append(d)
        return out


    def add_selected_order_to_asm2000(self, copies_number, rowData, selRowData):
        seq_list, names_list, amount_list, cpg_list, pos_list, order_id_list, purif_type \
            = [], [], [], [], [], [], []

        support_type_list = []
        purif_click_type_list = {'cart': [], 'hplc': [], 'lcms': [], 'click': []}

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

            support_type_list.append(self.get_support_type(s))
            purif_type_click = self.get_purif_click_type(s)
            for key in purif_type_click.keys():
                purif_click_type_list[key].append(purif_type_click[key])

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
            'Support type': support_type_list,#['biocomma_1000' for i in range(1, len(names_list) + 1)],
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

            'Do LCMS': purif_click_type_list['lcms'],#[False for i in range(1, len(names_list) + 1)],
            'Do synth': [True for i in range(1, len(names_list) + 1)],
            'Do cart': purif_click_type_list['cart'],#[False for i in range(1, len(names_list) + 1)],
            'Do hplc': purif_click_type_list['hplc'],#[False for i in range(1, len(names_list) + 1)],
            'Do paag': [False for i in range(1, len(names_list) + 1)],
            'Do sed': [False for i in range(1, len(names_list) + 1)],
            'Do click': purif_click_type_list['click'],#[False for i in range(1, len(names_list) + 1)],
            'Do subl': [True for i in range(1, len(names_list) + 1)],
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
        if len(rowData) == 1:
            if rowData[0]['#'] == 0:
                rowData = []
        if len(rowData) > 0:
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
                r5 = accord[accord['Modification'] == m]['ul on step'].max()
                r10 = 1#accord[accord['Modification'] == m]['ul on step, 10mg'].max()
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
                #accord.loc[accord['Modification'] == m, 'Amount 10mg, ml'] = round(vol10, round_n)
                accord.loc[accord['Modification'] == m, 'Amount 5mg, g'] = round(conc * vol5, round_n)
                #accord.loc[accord['Modification'] == m, 'Amount 10mg, g'] = round(conc * vol10, round_n)
            else:

                r5 = accord[accord['Modification'] == mod]['ul on step'].max()
                r10 = 1#accord[accord['Modification'] == mod]['ul on step, 10mg'].max()
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
                #accord.loc[accord['Modification'] == mod, 'Amount 10mg, ml'] = round(vol10, round_n)
                accord.loc[accord['Modification'] == mod, 'Amount 5mg, g'] = round(conc * vol5, round_n)
                #accord.loc[accord['Modification'] == mod, 'Amount 10mg, g'] = round(conc * vol10, round_n)

        total_count = sum(self.amidites_count.values())
        for mod, data in zip(accord['Modification'], accord['ul on step']):
            if mod in ['DEBL', 'ACTIV', 'CAPA', 'CAPB', 'OXID', 'R2', 'W1', 'W2']:
                accord.loc[accord['Modification'] == mod, 'Amount 5mg, ml'] = total_count * data / 1000

        return accord.to_dict('records')

    def get_pos_list(self, start):
        pos_list = []
        for j in range(1, 13):
            for i in 'A B C D E F G H'.split(' '):
                pos_list.append(f'{i}{j}')
        return pos_list[pos_list.index(start):]

    def get_pos_list_transposed(self, start):
        pos_list = []
        for i in 'A B C D E F G H'.split(' '):
            for j in range(1, 13):
                pos_list.append(f'{i}{j}')
        return pos_list[pos_list.index(start):]

    def rename_pos(self, selrowData, rowData, transposed=False):
        first = selrowData[0]
        selDF = pd.DataFrame(selrowData)
        DF = pd.DataFrame(rowData)

        synth_number = first['Synt number']
        name = first['Position']

        if transposed:
            pos_list = self.get_pos_list_transposed(name)
        else:
            pos_list = self.get_pos_list(name)

        #print(pos_list, len(pos_list), selDF.shape[0])

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

    def map_yield_analysis(self, map):
        if len(map)>0:
            df = pd.DataFrame(map)
            if 'Status' not in list(df.keys()):
                df['Status'] = 'none'
            df = df[df['Status'] == 'finished']
            df['amount, oe'] = df['Dens, oe/ml'].astype('float') * df['Vol, ml'].astype('float')
            df['CPG, mg'] = df['CPG, mg'].str.extract('(\d+)')
            df['CPG, mg'] = df['CPG, mg'].astype('int')
            if 'Support type' not in list(df.keys()):
                df['Support type'] = 'biocomma_1000'

            df_g = df.groupby(['Order id']).agg({'amount, oe': 'sum', 'CPG, mg': 'sum', 'Sequence': 'first',
                                                  'Support type': 'first'})

            df_g.reset_index(inplace=True)

            nmol_list, capasity_list, lenght_list = [], [], []
            for seq, oe, support in zip(df_g['Sequence'], df_g['amount, oe'], df_g['Support type']):
                if support.lower() in list(support_base().support_capasity.keys()):
                    capasity_list.append(support_base().support_capasity[support.lower()])
                else:
                    capasity_list.append(50.)
                oligo = mmo.oligoNASequence(seq)
                lenght_list.append(oligo.size())
                ext = oligo.getExtinction()
                if ext > 0:
                    nmol_list.append(oe * 1e6 / oligo.getExtinction())
                else:
                    nmol_list.append(0.)

            df_g['amount, nmol'] = nmol_list
            df_g['capasity'] = capasity_list
            df_g['lenght'] = lenght_list
            df_g['amount, max'] = df_g['CPG, mg'] * df_g['capasity']
            df_g['yield, %'] = df_g['amount, nmol'] * 100 / df_g['amount, max']

            stage_yield = []
            for y, l in zip(df_g['yield, %'], df_g['lenght']):
                stage_yield.append((y/100)**(1/l))

            df_g['stage yield, %'] = stage_yield
            df_g['stage yield, %'] = df_g['stage yield, %'] * 100

            return df_g['yield, %'].mean(), df_g['stage yield, %'].mean()
        else:
            return 0, 0

    def get_oligomaps(self, map_yield=False):
        self.all_not_fin_oligos = []
        self.oligo_map_id = -1
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
                #d['map data'] = pd.DataFrame(json.loads(r[4]))

                if map_yield:
                    y, s_y = self.map_yield_analysis(json.loads(r[4]))
                    d['avg yield, %'] = round(y, 1)
                    d['avg stage yield, %'] = round(s_y, 1)

                df = pd.DataFrame(json.loads(r[4]))
                if 'Status' in list(df.keys()):
                    self.all_not_fin_oligos.extend(df[df['Status'] != 'finished'].to_dict('records'))
                    d['Finished'] = df[df['Status'] == 'finished'].shape[0]
                else:
                    d['Finished'] = df.shape[0]
                d['Total'] = df.shape[0]
                if 'Wasted' in list(df.keys()):
                    w_df = df[df['Wasted'] == True]
                    d['Wasted'] = w_df.shape[0]
                else:
                    d['Wasted'] = 0
                out.append(d)
            return out
        else:
            return []

    def get_actual_maps(self):
        self.oligo_map_id = -1
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
                        d['Finished'] = row['Finished']
                        d['Total'] = row['Total']
                        d['Wasted'] = row['Wasted']
                        out.append(d)
            return out
        else:
            return []

    def get_actual_stat_maps(self):
        ret = {'wasted %': 0., 'total wells': 0}
        tab = self.get_oligomaps()
        orders = pd.DataFrame(self.get_orders_by_status('finished'))
        if len(tab) > 0:
            df = pd.DataFrame(tab)
            ret['wasted %'] = f"Wasted %: {round(df['Wasted'].sum() * 100/ df['Total'].sum(), 0)}"
            ret['total wells'] = f"Total wells: {df['Total'].sum()} / Total oligos: {orders.shape[0]}"
        return ret

    def update_all_actual_status(self):
        maps = self.get_oligomaps()
        df = pd.DataFrame(maps)
        df.sort_values('#', ascending=False, inplace=True)
        df.reset_index(inplace=True)
        df = df.loc[:4]
        maps = df.to_dict('records')
        for row in maps:
            map, acc_tab, m1, m2  = self.load_oligomap([row])
            self.update_order_status(map)

    def get_oligomaps_data(self):
        self.oligo_map_id = -1
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
                df = pd.DataFrame(d['map data'])
                if 'Status' in list(df.keys()):
                    d['Finished'] = df[df['Status'] == 'finished'].shape[0]
                else:
                    d['Finished'] = df.shape[0]
                d['Total'] = df.shape[0]
                if 'Wasted' in list(df.keys()):
                    d['Wasted'] = df[df['Wasted'] == True].shape[0]
                    #print(d['Wasted'])
                else:
                    d['Wasted'] = 0
                out.append(d)
            return out
        else:
            return []

    def get_solutions_history(self):

        url = f'{self.api_db_url}/get_all_tab_data/{self.solutions_db_name}/preparation_history'
        ret = requests.get(url, headers=self.headers())

        url = f'{self.api_db_url}/get_all_tab_data/{self.solutions_db_name}/compounds'
        comp = requests.get(url, headers=self.headers())

        url = f'{self.api_db_url}/get_all_tab_data/{self.stock_db_name}/users'
        users = requests.get(url, headers=self.headers())

        comp_list = []
        if comp.status_code == 200:
            for r in comp.json():
                d = {}
                d['#'] = r[0]
                d['Name'] = r[1]
                d['unicode'] = r[2]
                d['Composition_'] = r[3]#str(json.loads(r[3]))
                d['Composition'] = str(json.loads(r[3]))
                d['Description'] = r[5]
                comp_list.append(d)

        comp_df = pd.DataFrame(comp_list)

        self.user_list = []
        if users.status_code == 200:
            for r in users.json():
                d = {}
                d['name'] = r[1]
                d['telegram_id'] = r[2]
                d['pin'] = r[4]
                self.user_list.append(d)
        user_df = pd.DataFrame(self.user_list)

        out = []
        if ret.status_code == 200:
            for r in ret.json():
                d = {}
                d['#'] = r[0]
                d['unicode'] = r[1]
                d['Name'] = comp_df[comp_df['unicode'] == d['unicode']]['Name']
                d['Volume, ml'] = r[2]
                d['Date'] = r[5]
                d['User'] = user_df[user_df['telegram_id'] == r[6]]['name']
                d['Description'] = comp_df[comp_df['unicode'] == d['unicode']]['Description']
                out.append(d)

        return out, comp_list

    def culc_solution_compose(self, rowdata, sel_rowdata, volume):
        out = []

        vol = 500
        if volume != '':
            vol = int(volume)

        for row in rowdata:
            if len(sel_rowdata) > 0:
                d = row.copy()
                if sel_rowdata[0]['#'] == row['#']:

                    comp = json.loads(row['Composition_'])
                    res = {}
                    for k in comp.keys():
                        kk = list(comp[k].keys())[0]
                        if kk == '%':
                            res[k] = f"{vol * comp[k][kk] / 100} ml"
                        else:
                            res[k] = f"{vol * comp[k][kk]} g"

                    d['Culculation'] = str(res)

                    out.append(d)
                else:
                    d['Culculation'] = ''
                    out.append(d)
            else:
                out.append(row)
        return out

    #def get_tg_id(self, pin):

    def prepare_solution(self, sel_rowdata, volume):
        for row in sel_rowdata:
            if row['Culculation'] != '':
                df = pd.DataFrame(self.user_list)
                tg_id = df[df['pin'] == self.pincode]['telegram_id'].max()

                url = f'{self.api_db_url}/insert_data/{self.solutions_db_name}/preparation_history'
                ret = requests.post(url,
                                    json=json.dumps([
                                        row['unicode'],
                                        volume,
                                        'ml',
                                        1,
                                        str(datetime.now()),
                                        tg_id
                                    ]),
                                    headers=self.headers())

    def delete_preparation(self, selrows):
        for row in selrows:
            url = f"{self.api_db_url}/delete_data/{self.solutions_db_name}/preparation_history/{row['#']}"
            ret = requests.delete(url=url, headers=self.headers())


    def load_oligomap(self, seldata):
        self.oligo_map_id = -1
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

            url = f'{self.api_db_url}/get_all_tab_data/{self.maps_db_name}/main_map'
            ret = requests.get(url, headers=self.headers())
            indexs = [r[0] for r in ret.json()]

            self.oligo_map_id = max(indexs)

            data = []
            for row in rowData:
                d = row.copy()
                d['map #'] = self.oligo_map_id
                data.append(d)

            url = f"{self.api_db_url}/update_data/{self.maps_db_name}/main_map/{self.oligo_map_id}"
            r = requests.put(url,
                             json=json.dumps({
                                 'name_list': ['map_tab'],
                                 'value_list': [
                                     json.dumps(data)
                                 ]
                             })
                             , headers=self.headers())

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

    def get_low_amount_limit(self, amount):
        if amount.find('-')>-1:
            return float(amount[:amount.find('-')])
        else:
            return float(amount)

    def print_invoce_passport(self, selrowdata):
        out_tab = self.get_invoce_content(selrowdata)
        pass_tab = []
        out = []
        for row in out_tab:
            d = row.copy()
            #sequence = '[' + row["5'-end"] + ']' + row['Sequence'] + '[' + row["3'-end"] + ']'
            maps = self.search_maps_by_text(str(row['#']))
            if len(maps) > 0:
                df = pd.DataFrame(maps)
                df = df.sort_values(by='#', ascending=False)
                map_id = list(df['#'])[0]
                map = self.load_oligomap([{'#': map_id}])
                #print(map)
                df = pd.DataFrame(map[0])
                df = df[df['Order id'] == row['#']]
                df = df.sort_values(by='Dens, oe/ml', ascending=False)
                pass_tab.append(df.to_dict('records')[0])
                d['Exist, oe'] = round(pass_tab[-1]['Dens, oe/ml'] * pass_tab[-1]['Vol, ml'], 0)
            else:
                d['Exist, oe'] = 0.
            limit = self.get_low_amount_limit(d['Amount, oe'])
            d['sufficiency'] = d['Exist, oe'] - limit
            out.append(d)
        pass_tab = self.print_pass(pass_tab, 'invoce_pass.csv')
        return pass_tab, out

    def update_send_invoce_data(self, rowdata):
        param_list = []
        for row in rowdata:
            param_list.append({'id': row['#'], 'send_param': json.dumps({'send': row['send']})})
        if len(param_list) > 0:
            url = f"{self.api_db_url}/send_invoces_update/{self.db_name}"
            #print(json.dumps(param_list))
            ret = requests.put(url, json=json.dumps(param_list), headers=self.headers())

    def  print_pass(self, rowData, filename):
        out_tab = []
        index_ = 1
        for row in rowData:
            o = mmo.oligoNASequence(row['Sequence'])
            d = {}
            d['#'] = index_
            index_ += 1
            d['Position'] = row['Position']
            d['Name'] = row['Name'] + f"  ({row['Synt number']}_{row['Position']})"
            d['Sequence'] = row['Sequence']
            d['Amount,_oe'] = int(round(row['Dens, oe/ml'] * row['Vol, ml'], 0))
            if o.getExtinction() > 0:
                d['Amount,_nmol'] = int(round(d['Amount,_oe'] * 1e6 / o.getExtinction(), 0))
            else:
                d['Amount,_nmol'] = 0.
            d['Desolving'] = int(d['Amount,_nmol'] * 10)

            d['Purification'] = row['Purif type']
            d['order_ID'] = row['Order id']
            d['Status'] = row['Status']
            try:
                d['Mass,_Da'] = round(o.getAvgMass(), 2)
            except:
                d['Mass,_Da'] = 'unknown modiff'
            d['Extinction'] = o.getExtinction()

            out_tab.append(d)
        df = pd.DataFrame(out_tab)
        df.to_csv(filename, sep=';')

        return out_tab

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

    def update_support_type_amount(self, rowdata, sel_rowdata, supp_type='', supp_amount=''):
        sel_id_list = list(pd.DataFrame(sel_rowdata)['#'])
        out = []
        for row in rowdata:
            d = row.copy()
            if row['#'] in sel_id_list:
                if supp_type != '':
                    d['Support type'] = supp_type
                if supp_amount != '':
                    d['CPG, mg'] = supp_amount
            out.append(d)
        return out

    def set_sample_volume(self, rowdata, sel_rowdata, volume):
        sel_id_list = list(pd.DataFrame(sel_rowdata)['#'])
        out = []
        for row in rowdata:
            d = row.copy()
            if row['#'] in sel_id_list:
                try:
                    d['Vol, ml'] = float(volume)
                except:
                    d['Vol, ml'] = 1.
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
        #print(row.keys())
        #if 'Wasted' in list(row.keys()):
        #    if row['Wasted']:
        #        status = 'in queue'
        return status

    def update_oligomap_status(self, rowData, accordrowdata):
        if len(rowData) > 0:
            if 'map #' in list(rowData[0].keys()):
                for row in rowData:
                    if row['map #'] != '':
                        self.oligo_map_id = int(row['map #'])
                        print(f'MAP ID: {self.oligo_map_id}')
                        break
        if self.oligo_map_id > -1:
            out = []
            for row in rowData:
                out.append(row)
                out[-1]['Date'] = datetime.now().date().strftime('%d.%m.%Y')
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

    def update_order_status(self, rowData, selRowdata):
        df = pd.DataFrame(selRowdata)
        if len(rowData) > 0:
            for row in rowData:
                if df.shape[0] > 0:
                    if row['#'] in list(df['#']):
                        order_id = row['Order id']
                        order_date = row['Date']
                        order_status = row['Status']
                    else:
                        order_id = '###'
                else:
                    order_id = row['Order id']
                    order_date = row['Date']
                    order_status = row['Status']

                if order_id != '###':
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
        lna_count = 0
        for seq in df['Sequence']:
            oligo = mmo.oligoNASequence(seq)
            oligo_len = oligo.size()
            oligo_tab = oligo.getSeqTabDF()
            oligo_df = oligo_tab[oligo_tab['prefix'] == '+']
            lna_count += oligo_df.shape[0]
            len_list.append(oligo_len - oligo_df.shape[0])
        df['Lenght'] = len_list

        self.df_tab.loc[self.df_tab['Sequence'] != '', 'Lenght'] = len_list

        sum_ = df['Lenght'].sum()
        price_ = self.price_tab[self.price_tab['Unit'] == 'simple N']['Price, RUB'].max()
        lna_price_ = self.price_tab[self.price_tab['Unit'] == 'LNA']['Price, RUB'].max()

        self.price_tab.loc[self.price_tab['Unit'] == 'simple N', 'Number'] = sum_
        self.price_tab.loc[self.price_tab['Unit'] == 'simple N', 'Sum, RUB'] = sum_ * float(price_)

        self.price_tab.loc[self.price_tab['Unit'] == 'LNA', 'Number'] = lna_count
        self.price_tab.loc[self.price_tab['Unit'] == 'LNA', 'Sum, RUB'] = lna_count * float(lna_price_)

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
        params = json.dumps({'send': False})
        r = requests.post(url, json=json.dumps([invoce, client, params]), headers=self.headers())

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

    def show_history_data(self):
        hist, hist_data = [], []

        url = f"{self.api_db_url}/get_all_tab_data/{self.hist_db_name}/main_tab"
        r = requests.get(url, headers=self.headers())

        for row in r.json():
            d = {}
            d['#'] = row[0]
            d['User'] = row[1]
            d['Date'] = row[2]
            d['Time'] = row[3]
            d['URL'] = row[4]
            d['Remote addr'] = row[5]
            hist.append(d)

        url = f"{self.api_db_url}/get_all_tab_data/{self.hist_data_db_name}/main_tab"
        r = requests.get(url, headers=self.headers())

        for row in r.json():
            d = {}
            d['#'] = row[0]
            d['User'] = row[1]
            d['Date'] = row[2]
            d['Time'] = row[3]
            d['URL'] = row[4]
            d['Data json'] = row[5]
            hist_data.append(d)

        return hist, hist_data

    def show_row_data_info(self, selrowdata):
        ret = ''
        if len(selrowdata) > 0:
            data = json.loads(selrowdata[0]['Data json'])
            ret = f"data type: {type(data)} "
            if type(data) == dict:
                ret += f" keys: {data.keys()}"
            return ret
        return ret

    def show_map_tab_data_info(self, selrowdata):
        out = []
        if len(selrowdata) > 0:
            url = selrowdata[0]['URL']
            data = json.loads(selrowdata[0]['Data json'])
            if url.find('update_data/asm2000_map') > -1 and type(data) == dict:
                out = json.loads(data['value_list'][0])
            return out
        return out

    def backup_map_data(self, selrowdata):
        out = []
        if len(selrowdata) > 0:
            url = selrowdata[0]['URL']
            data = json.loads(selrowdata[0]['Data json'])
            if url.find('update_data/asm2000_map') > -1 and type(data) == dict:
                out = json.loads(data['value_list'][0])
                url = selrowdata[0]['URL']
                r = requests.put(url, json=selrowdata[0]['Data json'], headers=self.headers())
            return out
        return out

    def generate_history_dict(self):
        history_dict = {}
        hist, hist_data = self.show_history_data()
        data = pd.DataFrame(hist_data)
        data = data[data['URL'].str.contains("update_data/asm2000_map")]
        date_list = list(data['Date'].unique())
        for date in date_list:
            df = data[data['Date'] == date]
            map_list = list(df['URL'].unique())
            for url in map_list:
                map_df = df[df['URL'] == url]
                map_df.sort_values(by='Time', ascending=False, inplace=True)
                map_data = json.loads(json.loads(list(map_df['Data json'])[0])['value_list'][0])
                #print(map_data)
                for row in map_data:
                    if row['Order id'] in list(history_dict.keys()):
                        history_dict[row['Order id']].append({'Date': date, 'Status': row['Status']})
                    else:
                        history_dict[row['Order id']] = []
                        history_dict[row['Order id']].append({'Date': date, 'Status': row['Status']})
        return history_dict

    def get_invoce_history(self, invoce_id):
        tab = pd.DataFrame(self.get_all_invoces())
        tab = tab[tab['#'] == invoce_id]
        data = self.get_invoce_content(tab.to_dict('records'))
        #self.hist_dict = self.generate_history_dict()
        #print(hist_dict.keys())
        hist_data = []
        for row in data:
            if row['#'] in list(self.hist_dict.keys()):
                for i in self.hist_dict[row['#']]:
                    hist_data.append(i)
        df = pd.DataFrame(hist_data)
        if df.shape[0] > 0:
            min_date = df['Date'].min()
            max_date = df['Date'].max()
        else:
            min_date = datetime.now().date().strftime('%d.%m.%Y')
            max_date = datetime.now().date().strftime('%d.%m.%Y')
        return min_date, max_date

    def set_invoce_real_timing(self, rowdata, selrows):
        out = []
        selections = [int(i) for i in list(pd.DataFrame(selrows)['#'].unique())]
        if len(selrows) > 0:
            self.hist_dict = self.generate_history_dict()
        for row in rowdata:
            if row['#'] in selections:
                d = row.copy()
                min_date, max_date = self.get_invoce_history(row['#'])
                d['input date'] = min_date
                d['out date'] = max_date
                out.append(d)
            else:
                out.append(row)
        return out

    def oligomap_history_to_date(self, date):
        hist, hist_data = self.show_history_data()
        print(date)
        data = pd.DataFrame(hist_data)
        data = data[data['Date'] == date]
        data = data[data['URL'].str.contains("update_data/asm2000_map")]
        urls = list(data['URL'].unique())
        #print(urls)
        hist_ids = []
        for url in urls:
            p_data = data[data['URL'] == url]
            p_data.sort_values(by='Time', ascending=False, inplace=True)
            hist_ids.append(list(p_data['#'])[0])
        out_tab = []
        order_list = []
        for id in hist_ids:
            df = data[data['#'] == id]
            time = df['Time'].max()
            map = json.loads(df['Data json'].max())
            #print(id)
            #print(json.loads(map['value_list'][0]))
            for row in json.loads(map['value_list'][0]):
                d = {}
                d['Date'] = date
                d['Time'] = time
                d['User'] = df['User'].max()
                d['Name'] = row['Name']
                d['Order id'] = row['Order id']
                d['Synt number'] = row['Synt number']
                d['Position'] = row['Position']
                d['Sequence'] = row['Sequence']
                d['Status'] = row['Status']
                d['Wasted'] = row['Wasted']
                order_list.append(row['Order id'])
                out_tab.append(d)

        url = f"{self.api_db_url}/get_all_invoces_by_orders/{self.db_name}"
        r = requests.get(url, json=json.dumps(order_list), headers=self.headers())

        #print(r.json())

        out_data_list = []
        for row, invoce in zip(out_tab, r.json()):
            d = row.copy()
            d['client'] = invoce['client']
            d['invoce'] = invoce['invoce']
            out_data_list.append(d)
        return self.filtrate_oligomap_history_of_day(out_data_list, date)

    def filtrate_oligomap_history_of_day(self, hist_of_day_tab, date):
        hist_dict = self.generate_history_dict()
        #print(hist_dict[2685])
        out = []
        for row in hist_of_day_tab:
            df = pd.DataFrame(hist_dict[row['Order id']])
            df = df[df['Date'] < date]
            if df.shape[0] > 0:
                df.sort_values(by='Date', ascending=False, inplace=True)
                last_status = list(df['Status'])[0]
                if last_status != row['Status']:
                    out.append(row)
            else:
                out.append(row)

        if len(out) > 0:
            df = pd.DataFrame(out)
            df_g = df.groupby('Order id').agg('first').reset_index()
            return df_g.to_dict('records')
        else:
            return out

    def return_scale_accord_tab(self, rowdata, scale):
        self.scale_dict = {'1 mg': 34., '3 mg': 40., '5 mg': 54.}
        out = []
        if self.check_pincode():
            for row in rowdata:
                d = row.copy()
                if row['Modification'] in 'A C G T'.split(' '):
                    #d['ul on step, 5mg'] = self.scale_dict[scale]
                    d['ul on step'] = self.scale_dict[scale]
                out.append(d)
            return out
        return rowdata



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

def extract_history_tab(from_date, to_date):
    orders_data = orders_db(db_IP='127.0.0.1', db_port='8012')
    orders_data.pincode = '1880'
    date = datetime.strptime(from_date, "%d.%m.%Y")
    date_end = datetime.strptime(to_date, "%d.%m.%Y")
    count = 0
    out = []
    while date_end >= date:
        count += 1
        print(count, date.date().strftime("%d.%m.%Y"), date_end.date().strftime("%d.%m.%Y"))
        #str_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date().strftime("%d.%m.%Y")
        try:
            out.extend(orders_data.oligomap_history_to_date(date.date().strftime("%d.%m.%Y")))
        except:
            pass
        date += timedelta(days=1)

    df = pd.DataFrame(out)
    df.to_csv('history_extract_1.csv', sep='\t')

    for row in out:
        print(row)

def hist_tab_stat():
    pass

def calc_oligo_cpg():
    model = oligo_amount_model('ACGTAACGTAACGACGTAACGTAACG', 0.10)
    print(model.get_cpg_mg('30-40', 42))


if __name__ == '__main__':
    #extract_history_tab('23.01.2025', '21.04.2025')
    calc_oligo_cpg()