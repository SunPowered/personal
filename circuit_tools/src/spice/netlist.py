'''
@package spice.netlist
@file spice/netlist.py
@brief The SPICE netlist module
@author: timvb
'''
import os
import string
import re

from schematic.netlist import Netlist, NetlistError, generateNetlistFilePath
from utils import config, log

_default_netlist_extension = config.DEFAULT_NETLIST_SPICE_EXTENSION
_netlist_scheme = 'spice-sdb'
_netlist_type = 'spice'

class SpiceNetlistError(NetlistError):
    pass
class SpiceNetlist(Netlist):
    '''
    @brief A SPICE netlist object.
    @details Takes a different default file extension than a regular netlist.
    Also has the ability to handle variables, parsing and substitution into a temp path
    @todo add ability to modify control block to customize simulation control @par This would 
    consist of adding and removing any sim commands such as tran ac as well as controlling 
    any vectors written to a raw file
    '''
    _netlist_scheme = _netlist_scheme

    def __init__(self, *args, **kwargs):
        '''
        @note Takes the same parameters as a schematic.netlist.Netlist object
        '''
        if not kwargs.get('logger', None):
            kwargs['logger']=log.getDefaultLogger('spice.netlist.SpiceNetlist')
            
        Netlist.__init__(self, *args, netlist_scheme=_netlist_scheme, **kwargs)
        self.setType(_netlist_type)  
        self._default_netlist_extension = _default_netlist_extension
        #Template
        self.template = string.Template(open(self.file_path, 'r').read())   
        
        #temp file_path
        path, ext = os.path.splitext(self.file_path)
        self.temp_file_path = path + '.tmp' + ext
        self.temp_file_name = os.path.split(self.temp_file_path)[1]
        
        #Regex
        self.comment_re = r"\*"
        self.variable_re = re.compile(r"^[^"+self.comment_re+r"].*" + config.VARIABLE_FLAG_RE + r"(\w+)", re.M)
        
        #Parse variables
        self.parseVariables()
        
    def getTemplate(self):
        '''
        @brief return the current netlist template object
        @return string Template object
        '''
        return self.template
           
    def getTempFilePath(self):
        '''
        @brief return the temporary file path
        @return str file path
        '''
        return self.temp_file_path
    
    def getTempFileName(self):
        '''
        @brief return the temporary file name
        @return str file path 
        '''
        return self.temp_file_name
    
    def getVariables(self):
        '''
        @brief return the circuit variables
        @return list 
        '''
        return self.variables
    
    def parseVariables(self):
        '''
        @brief parses the current netlist file and returns a list of variables in the file
        @return list
        '''
        try:
            variables = self.variable_re.findall(open(self.file_path, 'r').read())
        except Exception, msg:
            self.logger.error("Error occured matching variables in Netlist file")
            raise NetlistError(msg)
        
        self.variables = variables
        self.variables.sort()
        return self.variables
        
    def substituteVariables(self, variables):
        '''
        @brief A safe substitution of variables into a netlist file.  
        @param variables A dict of variable mappings to substitute
        @return str file path
        @details Saves to the temp file attribute
        '''
        
        #Remove temp file if it exists
        try:
            os.remove(self.temp_file_path)
        except:
            pass
        
        #template = string.Template(open(self.file_path, 'r').read())
        
        try:
            open(self.temp_file_path, 'w').write(self.getTemplate().safe_substitute(variables))
        except Exception, msg:
            self.logger.error("Unexpected error occurred during temp file write: %s"%(msg))
            
        return self.temp_file_path

def generateSpiceNetlistFilePath(file_path):
    '''
    @brief helper function to convert a file path to a netlist file.
    @param file_path The file path of the circuit file to convert
    @return str A SPICE compatible file path
    @details Useful in converting a circuit to a netlist
    '''
    return generateNetlistFilePath(file_path, default_extension=_default_netlist_extension)    