'''
@package utils.config
@author timvb
@file utils/config/__init__.py
@brief Project wide configuration
'''

#Project Settings
PROJECT_NAME = 'TvB Circit Tools'
#Circuit and netlist file variable flags
VARIABLE_FLAG = "$"
VARIABLE_FLAG_RE = r"\$"

#Array Configurations
DEFAULT_ARRAY_LENGTH = 10
'''
make all other config modules available from the top package
'''

from spice_config import *
from netlist_config import *
from bom_config import *