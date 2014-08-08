cirklon.py
==========

Python utilities for the Sequentix Cirklon sequencer



Description
------------

This module provides a few simple classes for working with Cirkon instrument definitions as well as a command line program for creating an instrument definition file from a CSV formatted file of MIDI CC numbers and corresponding labels.

Requirements
------------

Currently this module only uses modules from the Python Standard Library.  It uses ordered dictionaries from the `collections` module, and thus requires Python 2.7 or newere.


Usage
-----

```
python cirklon.py input.csv -o myinstr.cki
```

In the absence of an input file, the program will read from stdin.  If no output file is specified, the instrument definition JSON data is written to stdout.

Type `python cirklon.py -h` for the full set of command line options.



Example
-------
To test the module, I have included a CSV file (`novation-KSRack-cc.csv`) with MIDI CC mappings for the Novation KS series synths (KS4, KS5, KS Rack). Here's how to process the file, including optional arguments:

```
python cirklon.py --name="KSRack" --port=2 --multi novation-KSRack-cc.csv > KSRack.cki
```