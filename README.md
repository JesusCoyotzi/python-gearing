# python-gearing
A very simple python utility to draw involute, metric spur gears. 
Simply run from the command line:
```bash
python gears.py -h
usage: gears.py [-h] --module MODULE --n N [--store] [--noplot]

Python involute gear generation

optional arguments:
  -h, --help       show this help message and exit
  --module MODULE  Gear module, only gears with the same module can mesh
  --n N            Number of teeth
  --store          Store gear as plain text
  --noplot         Plot Gear
```
The --store parameter allows to store the list of 2D points that conform the gear to a text file on disk. 
The name of the file is gear-{module}-{teeth}.gear. 

## Dependencies
Python3 and Numpy. That is all!

## TODO
Perhaps adding support for DXF export
