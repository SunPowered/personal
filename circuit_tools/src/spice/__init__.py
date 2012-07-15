'''
@package spice
@file spice/__init__.py
@brief Custom spice related modules
'''
import re

__all__ = ['simulation', 'netlist', 'circuit']

class Callable:
    """@brief Simple class to add support for static class methods."""
    def __init__(self, anycallable):
        self.__call__ = anycallable

class NumberConverter:
    """
    @brief This class converts a number with SPICE suffix into
    a real float.  
    @details
    It is case insensitive.
    If the suffix is not found, it assumed to be UNITS and is ignored."""

    num_re = re.compile("([+-]?[\de\-\.]+)(\w*)")
    suffix_dict = {'': 1,
           'g':1e9,
                   'meg':1e6,
                   'k':1e3,
                   'm':1e-3,
                   'u':1e-6,
                   'n':1e-9,
                   'p':1e-12} 

    def isnumber(num):
           return NumberConverter.num_re.match(num) is not None
    
    isnumber = Callable(isnumber)

    def convert(num):
        '''
        @brief converts a spice number to a float value
        @param num A str of a SPICE number i.e. '1.6k'
        @return float 
        '''
        match_obj = NumberConverter.num_re.match(num)
        assert match_obj is not None
        number = match_obj.group(1)
        suffix = match_obj.group(2)
        if not NumberConverter.suffix_dict.has_key(suffix):
            warning = "Invalid suffix '%s'. IGNORED!" % suffix
            suffix = ''
            print warning
        return float(number) * NumberConverter.suffix_dict[suffix]        
    convert = Callable(convert)