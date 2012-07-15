'''
@package utils.config.bom_config
@author timvb
@file utils/config/bom_config.py
@brief Bill Of Materials configuration
'''

#BOM Circuit Parse Model
BOM_PARSE_MODEL = { #Everything gets added to a BOM parse unless a flag below is found 
                   "IGNORED_ATTRIBUTES": ['symversion', 'author', ], #global attributes to ignore
                   "FLAGGED_DEVICES": ['INPUT', 'OUTPUT', 'NET'], #devices to flag a component for ignore
                   "FLAGGED_ATTRIBUTES": ['graphical'], #attributes to flag a component for ignore
                   "REQUIRED_ATTRIBUTES": ['device', 'manufacturer', 'part-number', 'value'] #all BOM components will have these attributes, even if its None
                   }