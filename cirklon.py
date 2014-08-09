#!/usr/bin/env python

"""
cirklon.py

Copyright (c) 2014 Paul M. Magwene

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import csv
import json
from collections import OrderedDict


track_controls = ["pgm", "quant%", "note%","noteC","velo%","veloC",
                  "leng%","tbase","octave","knob1","knob2"]

class Instrument(OrderedDict):
    def __init__(self, name, port=1, channel=1, multi=False, no_xpose=True, no_fts=True):
        OrderedDict.__init__(self)
        self.name = name[:9]  # max instrument name is 9 chars
        self.track_values = OrderedDict()
        self.midi_details = OrderedDict()
        self.midi_details['midi_port'] = port
        self.midi_details['midi_chan'] = channel
        self.midi_details['multi'] = multi
        self.midi_details['no_xpose'] = no_xpose
        self.midi_details['no_fts'] = no_fts
        self.midi_details['track_values'] = self.track_values
        self[name] = self.midi_details
        self.current_slot = 0

    def __repr__(self):
        return json.dumps(self)

    def add_cc(self, slot, cc, label):
        nslot = int(slot)
        key = "slot_%d" % nslot
        val = OrderedDict([ ('MIDI_CC', cc), ('label', label[:6]) ])
        self.track_values[key] = val

    def add_track_control(self, slot, trkcontrol):
        nslot = int(slot)
        key = "slot_%d" % nslot
        val = OrderedDict([ ('track_control', trkcontrol)])
        self.track_values[key] = val

    def add_slots(self, iterable):
        for row in iterable:
            nslot = self.current_slot + 1
            cc, label = row[0], row[1]
            if cc == "---":
                pass
            elif cc in track_controls:
                self.add_track_control(nslot, cc)
            else:
                cc = int(cc)
                self.add_cc(nslot, cc, label)
            self.current_slot += 1

    def skip_slot(self):
        self.current_slot += 1



class InstrumentDef(OrderedDict):
    def __init__(self, *args):
        OrderedDict.__init__(self, *args)
        self.instruments = []

    def add(self, instrument):
        self.instruments.append(instrument)
        self[instrument.name] = instrument.midi_details
        
    def to_json(self):
        instrument_dict = {'instrument_data': self}
        return json.dumps(instrument_dict, indent=4)
        
    def write_json(self, fname):
        f = open(fname,'w')
        f.write(self.to_json())
        f.close()



def instrument_from_csv(fname, name='Generic', port=1, channel=1, 
                            multi=False, no_xpose=False, no_fts=False, has_header=True):
    if isinstance(fname, str):
        fname = open(fname, 'rU')
    slotdata = csv.reader(fname)

    if has_header:
        next(slotdata, None)  # iterate past header field
    instrument = Instrument(name, port, channel, multi, no_xpose, no_fts)
    instrument.add_slots(slotdata)
    idef = InstrumentDef()
    idef.add(instrument)
    return idef



def slot_hack(instrdef):
    """An ugly hack to deal with limitation of 96 track values"""
    jsonstr = instrdef.to_json()
    instr = instrdef.instruments[0]
    if instr.current_slot <= 96:
        return jsonstr
    for i in range(97, instr.current_slot+1):
        hackslot = "slot_%d" % i
        jsonstr = jsonstr.replace(hackslot, "slot_96")
    return jsonstr




import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a Cirklon instrument definition file from a CSV file.')

    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help="CSV formatted file (or stdin)")
    parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help="Output filename (or stdout)")

    parser.add_argument('-n','--name' ,nargs='?', type=str, default="Generic",
                        help="Name of instrument")
    parser.add_argument('--port', nargs='?', type=int, default=1, help="MIDI port (default=1)")
    parser.add_argument('--channel', nargs='?', type=int, default=1, help="MIDI channel (default=1)")
    parser.add_argument('--multi', action="store_true",
                        help="Instrument responds to multiple channels [multitimbral] (default=False)")
    parser.add_argument('--noxpose', action="store_true",
                        help="Disable pattern transposition (default=False)")
    parser.add_argument('--nofts', action="store_true",
                        help="Disable force-to-scale (default=False)")
    parser.add_argument('--noheader', action="store_false",
                        help="Specifies whether the CSV file has a header row (default=True)")

    args = parser.parse_args()
    

    instrumentdef = instrument_from_csv(args.infile, name=args.name, 
                                        port=args.port, channel=args.channel,
                                        multi=args.multi, no_xpose=args.noxpose, 
                                        no_fts=args.nofts, has_header=args.noheader)

    jsonstr  = slot_hack(instrumentdef)
    args.outfile.write(jsonstr)

