'''
Created on 2012-07-08

@author: timvb

Holds all project wide configuration options.  Folders and such
'''

#Circuit and netlist file variable flags
VARIABLE_FLAG = "$"
VARIABLE_FLAG_RE = r"\$"

#default extensions
DEFAULT_NETLIST_EXTENSION = '.net'
DEFAULT_NETLIST_SPICE_EXTENSION = '.cir'

#BOM Circuit Parse Model
BOM_PARSE_MODEL = { #Everything gets added to a BOM parse unless a flag below is found 
                   "IGNORED_ATTRIBUTES": ['symversion', 'author', ], #global attributes to ignore
                   "FLAGGED_DEVICES": ['INPUT', 'OUTPUT', 'NET'], #devices to flag a component for ignore
                   "FLAGGED_ATTRIBUTES": ['graphical'], #attributes to flag a component for ignore
                   "REQUIRED_ATTRIBUTES": ['device', 'manufacturer', 'part-number'] #all BOM components will have these attributes, even if its None
                   }
                   
                   
