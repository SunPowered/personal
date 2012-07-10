'''
Created on 2012-07-08

@author: timvb
'''
import os
#import string
#import re

from utils import log, config

_default_netlist_extension = config.DEFAULT_NETLIST_EXTENSION

class NetlistError(Exception):
    pass

class Netlist(object):
    '''
    Netlist object, required for simulations and much more
    
    @input:
        file_path - The file path of the current netlist
        name (Optional) - Assign a name to the netlist
        
    TODO: Implement a removal of any .INCLUDE .*.LIB statements from netlist
    '''   
    
    _netlist_scheme = 'geda'
    
    def __init__(self, file_path, name=None, logger=None, type_=None, netlist_scheme=None):
        #Logger init
        if not logger:
            self.logger = log.getDefaultLogger('circuit.Netlist')
        else:
            self.logger = logger
        
        #Name init
        if not name:
            try:
                self.name = os.path.splitext(os.path.split(file_path)[1])[0]
            except:
                self.logger.error("Error in split")
                raise NetlistError("Name could not be assigned")
        else:
            self.name = name
        
        #file_path init
        self.file_path = file_path
        if not os.path.isfile(file_path):
            raise NetlistError("File does not exist: %s"%(self.file_path))

        #type init
        self.setType(type_)
        self.setNetlistScheme(netlist_scheme)
        
        self._default_netlist_extension = _default_netlist_extension    
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
    def getType(self):
        return self.type_
    
    def setType(self, type_):
        self.type_ = type_
    
    def getNetlistScheme(self):
        return self.netlist_scheme
    
    def setNetlistScheme(self, netlist_scheme):
        self.netlist_scheme = netlist_scheme
            
    def getFilePath(self):
        return self.file_path
       
    def removeNetlistFile(self):
        '''
        removes the current file.  useful for cleanup operations after a batch process
        '''
        self.logger.debug("Removing file %s"%(self.getFilePath()))
        return os.remove(self.getFilePath())
    
def generateNetlistFilePath(file_path, default_extension=_default_netlist_extension):
    '''
    replaces the extension of the given file path with that defined in the configuration settings.
    
    Useful for 
    '''
    try:
        path, ext = os.path.splitext(file_path)
    except:
        return None
    
    return path + default_extension