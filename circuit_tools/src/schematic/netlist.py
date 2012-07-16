'''
@file schematic/netlist.py
@package schematic.netlist

@author timvb
@brief A module containing schematic netlist objects
@version 0.1.0
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
    @brief Netlist object, required for simulations and much more
  
    @todo Implement a removal of any .INCLUDE .*.LIB statements from netlist
    '''   
    
    _netlist_scheme = 'geda'
    
    def __init__(self, *args, **kwargs):
        '''
        @brief The Constructor method for a schematic.Netlist object
        @param args Optional Arguments @li @b file path The netlist file path 
        @parma kwargs Optional keyword arguments @li @b name Assign a name to the netlist
        @li @b logger Assign a custom logger object to the netlist
        @li @b type Assign a type  to the netlist (Maybe useless)
        @li @b  netlist_scheme Assign a gnetlist scheme to use for gnerating the netlist
        '''
        #Logger init
        self.logger = kwargs.get('logger', log.getDefaultLogger('schematic.netlist.Netlist'))
        
        self.setName(kwargs.get('name', ''))
        

        
        #file_path init
        if args:
            file_path = args[0]
        else:
            file_path = None
        self.setFilePath(file_path)
            
        #if not os.path.isfile(file_path):
        #    raise NetlistError("File does not exist: %s"%(self.file_path))

        #type init
        self.setType(kwargs.get('type', None))
        self.setNetlistScheme(kwargs.get('netlist_scheme', None))
        
        self._default_netlist_extension = _default_netlist_extension   
        
    def setFilePath(self, file_path):
        '''
        @brief sets the file path for the current netlist
        @param file_path
        ''' 
        if not file_path:
            return
        if not os.path.isfile(file_path):
            raise NetlistError('File does not exist: %s'%(file_path))
        if not self.getName():
            '''
            Auto-generate name if none already assigned
            '''
            self.setName(os.path.splitext(os.path.split(file_path)[1])[0])
        self.file_path = file_path
        
    def getFilePath(self):
        '''
        @brief get the file path
        @return the file path for the current netlist 
        '''
        return self.file_path
    
    def getName(self):
        '''
        @brief return the current name of the netlist
        @return a string
        '''
        return self.name
    
    def setName(self, name):
        '''
        @brief Set the current name of the netlist
        @param name The name to assign
        '''
        self.name = name
        
    def getType(self):
        '''
        @brief get the current netlist type
        @return a string
        '''
        return self.type_
    
    def setType(self, type_):
        '''
        @brief Sets the current netlist type
        @param type_ the type of the current netlist
        '''
        self.type_ = type_
    
    def getNetlistScheme(self):
        '''
        @brief Returns the gnetlist scheme to use while generating a new netlist
        @return a string 
        '''
        return self.netlist_scheme
    
    def setNetlistScheme(self, netlist_scheme):
        '''
        @brief Set the current netlist scheme
        @param netlist_scheme The netlist scheme to assign
        '''
        self.netlist_scheme = netlist_scheme
            
    def getFilePath(self):
        '''
        @brief Return the current netlist file path
        @return a string file path
        '''
        return self.file_path
       
    def removeNetlistFile(self):
        '''
        @brief removes the current netlist file from the file system.  
        @return the returned value from os.remove
        useful for cleanup operations after a batch process
        '''
        self.logger.debug("Removing file %s"%(self.getFilePath()))
        try:
            os.remove(self.getFilePath())
        except OSError:
            pass
    
def generateNetlistFilePath(file_path, extension=_default_netlist_extension):
    '''
    @brief replaces the extension of the given file path with that defined in the configuration settings.
    @param file_path The current file path to replace
    @param extension Assign an extension to the file.  
    Default is set in the utils.config.DEFAULT_NETLIST_EXTENSION module
    @return a string file path 
     
    '''
    try:
        path, ext = os.path.splitext(file_path)
    except:
        return ''
    
    return path + config.DEFAULT_NETLIST_EXTENSION