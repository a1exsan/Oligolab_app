

class asm2000_protocol():
    def __init__(self):
        self.template_filename = 'DNA_RNA_Thio_Prовes_03mg_template.pr2'
        self.set_SR_dict()

    def set_SR_dict(self):
        self.SR_dict = {}
        for f_p in 'a b c d e'.split(' '):
            for i in range(1,6):
                self.SR_dict[f'sr_{f_p}{str(i)}_m'] = str(5)
                self.SR_dict[f'sr_{f_p}{str(i)}_s'] = str(30)

    def change_SR_protocol(self):
        with open(f'asm2000_protocols/{self.template_filename}', 'r') as f:
            self.content = f.read()

        for key, value in zip(self.SR_dict.keys(), self.SR_dict.values()):
            s = '{' + str(key) + '}'
            self.content = self.content.replace(s, str(value))

            savefilename = self.template_filename.replace('template', 'working')
        with open(f'asm2000_protocols/{savefilename}', 'w') as f:
            f.write(self.content)


def test1():
    prot = asm2000_protocol()

    prot.SR_dict['sr_a1_m'], prot.SR_dict['sr_a1_s'] = 1, 10
    prot.SR_dict['sr_a2_m'], prot.SR_dict['sr_a2_s'] = 1, 10
    prot.SR_dict['sr_b1_m'], prot.SR_dict['sr_b1_s'] = 5, 30
    prot.SR_dict['sr_b2_m'], prot.SR_dict['sr_b2_s'] = 0, 50
    prot.SR_dict['sr_b3_m'], prot.SR_dict['sr_b3_s'] = 5, 30
    prot.SR_dict['sr_b4_m'], prot.SR_dict['sr_b4_s'] = 0, 50
    prot.SR_dict['sr_b5_m'], prot.SR_dict['sr_b5_s'] = 5, 30

    prot.change_SR_protocol()

if __name__ == '__main__':
    test1()
