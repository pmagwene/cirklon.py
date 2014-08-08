

import csv
import json


class CirklonInstrument(dict):
    def __init__(self, name, port=1, channel=1, multi=False):
        self.name = name
        self.port = port
        self.channel = channel
        self.multi = multi
        self.track_values = {}
        self.instrument_data = \
            {name: {'midi_port': port,
                    'midi_chan': channel,
                    'multi': multi,
                    'track_values': self.track_values
                    }
            }
        
    def add_cc(self, slot, ccnum, label):
        key = "slot_%d" % slot
        val = {'MIDI_CC':ccnum, 'label': label[:6]}
        self.track_values[key] = val
        
    def __repr__(self):
        return str(self.instrument_data)
        
        
    def to_json(self):
        instrument_dict = {'instrument_data': self.instrument_data}
        return json.dumps(instrument_dict, indent=4, sort_keys=True)
        
    def save_json(self, fname):
        f = open(fname,'w')
        f.write(self.to_json())
        f.close()


    def cc_from_csv(self, cvs_ccdict):
        for row in cvs_ccdict:
            self.add_cc(int(row['slot']), int(row['cc']), row['label'])



def csv_to_ccdict(fname, has_header=True):
    ccdict = csv.DictReader(open(fname,'r'), ['slot','cc', 'label'])
    if has_header:
        next(ccdict, None)  # skip the header
    return ccdict


def instrument_from_csv(fname, name, port=1, channel=1, multi=False):
    ccdict = csv_to_ccdict(fname)
    inst = CirklonInstrument(name, port, channel, multi)
    inst.cc_from_csv(ccdict)
    inst.save_json('%s.cki' % name)