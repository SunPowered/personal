'''
Created on 2012-07-08

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
    A SPICE netlist object.
    
    Takes a different default file extension than a regular netlist.
    Also has the ability to handle variables, parsing and substitution into a temp path
    '''
    _netlist_scheme = _netlist_scheme

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        if not kwargs.get('logger', None):
            kwargs['logger']=log.getDefaultLogger('spice.netlist.SpiceNetlist')
            
        Netlist.__init__(self, *args, netlist_scheme=_netlist_scheme, type_=_netlist_type, **kwargs)
        
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
        return self.template
           
    def getTempFilePath(self):
        return self.temp_file_path
    
    def getTempFileName(self):
        return self.temp_file_name
    
    def getVariables(self):
        return self.variables
    
    def parseVariables(self):
        '''
        parses the current netlist file and returns a list of variables in the file
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
        A safe substitution of variables into a netlist file.  Saves to the temp file attribute
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
    return generateNetlistFilePath(file_path, default_extension=_default_netlist_extension)    