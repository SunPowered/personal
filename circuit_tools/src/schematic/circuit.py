'''
@file schematic/circuit.py
@package schematic.circuit
@author timvb
@brief A module containing schematic circuit objects
@version 0.1.0

@details
This holds the general Circuit object

'''

import os

from utils import log, config, fs
from schematic.netlist import Netlist


class CircuitError(Exception):
    '''
    @brief Generic Circuit Error
    '''
    pass

class CircuitFileError(CircuitError):
    '''
    @brief Schematic File Error
    '''
    pass



class Circuit(object):
    '''
    @brief Contatiner for a Schematic Circuit object.      
    This low level object is intended to be subclassed for more detailed
    implementations.  
    
   
    @todo Add more doc
    '''


    def __init__(self, file_path, name=None, logger=None, netlist_cls=None):
        '''
        @brief Schematic Circuit Constructor  
        @param file_path The path to the circuit file
        @param name (Opt) An internal name to assign the to the circuit.  If none is provided, a name is auto generated from the file_path
        @param logger (Opt) Assign a custom logger object  
        @param netlist_cls (opt) The netlist class to assign to any generated netlists
        @throw CircuitFileError If the file_path does not point to an existing file or does not have a .sch extension      
        '''
        #Logging
        if not logger:
            self.logger = log.getDefaultLogger('circuit.Circuit')
        else:
            self.logger = logger
            
        #Check whether file exists
        if not os.path.isfile(file_path):
            raise CircuitFileError("file does not exist: %s"%(file_path))
        
        #Check .sch file type
        if os.path.splitext(file_path)[1] != ".sch":
            raise CircuitFileError("Given file must have a .sch extension")
        
        #
        #Set attributes
        #
        self.file_path = file_path
        self.file_name = os.path.split(file_path)[1]
        
        #Auto assign name if not provided
        self.name = name or os.path.splitext(self.file_name)[0]
        #Auto set netlist_cls to Netlist if not provided
        self.setNetlistClass(netlist_cls or Netlist)

    
    def setName(self, name):
        '''
        @brief sets the circuit name
        @param name A string name to assign
        '''
        self.name=name    
        
    def getName(self):
        '''
        @brief gets the circuit name
        @return A name string object
        '''
        return self.name
    
    def getFileName(self):
        '''
        @brief returns the currently stored circuit file name
        @return A file name string object
        '''
        return self.file_name
    
    def getFilePath(self):
        '''
        @brief returns the currently stored circuit file path
        @return A file path string object
        '''
        return self.file_path
    

    
    def _readFileData(self):
        '''
        @private
        @brief An internal helper method to read the data from the stored file path
        @return the entire file contents as a string
        '''
        return open(self.getFilePath(), 'r').read()
    

    def setNetlistClass(self, netlist_cls):
        '''
        @brief assign a netlist class to instantiate
        @param netlist_cls A child of schematic.Netlist
        @throw schematic.Circuit.CircuitError When netlist_cls is not a child
        of schematic.netlist.Netlist 
        '''
        
        if not isinstance(netlist_cls(), Netlist):
            raise CircuitError("Not a child of Netlist: %s"%(netlist_cls))
        self.netlist_cls = netlist_cls

    
    def getNetlistClass(self):
        '''
        @brief return the netlist class stored
        @return a child of schematic.Netlist
        '''
        return self.netlist_cls
    def _generateNetlist(self, *args, **kwargs):
        '''
        @private
        @brief Helper function to create a netlist, used by subclassed objects  
        @todo implement an stdout, stderr redirect during the gnetlist call. 
        Maybe have the user be able to define where she wants it, default is buffered
        and spit out in case of error 
        '''
        output_file_name = kwargs.get('output_file_name', self.getName() + config.DEFAULT_NETLIST_EXTENSION)

        if os.path.splitext(output_file_name)[1] == "":
            #No extension on the output file name, add the default
            self.logger.info("No extension found on output file name: %s.  Adding default extension, %s"%(output_file_name, self.default_netlist_extension))
            output_file_name = output_file_name + self.default_netlist_extension
        
        #File goes in same directory as this circuit
        #change the cwd to the circuit directory, to help with relative paths in schematics
        old_working_directory = os.getcwd()
        new_working_directory = fs.switchWDFromFilePath(self.getFilePath())
        
        output_file_path = os.path.join(new_working_directory, output_file_name)    
        scm_type = self.netlist_cls._netlist_scheme
        

        #Run gnetlist 
        n = ''
        self.logger.info("Generating netlist of circuit %s"%(self.getName()))
        cmd = "gnetlist -I -q -g %s -o %s %s"%(scm_type, output_file_path, self.file_path)
        if config.DEBUG:
            result = os.system(cmd)
        else:
            result = os.system(cmd + ' 2>&1')
            
        if result != 0:
            self.logger.error("Error occurred during netlist creation")
        else:
            if not fs.waitForFile(output_file_path):
                os.chdir(old_working_directory)
                raise CircuitError("Netlist file %s not created"%(output_file_path))
            n = self.netlist_cls(output_file_path, name=self.getName(), logger=self.logger)
            
        return n
    

    
    def generateNetlist(self, output_file_name=None, name=None):
        '''
        @brief calls gnetlist automatically filling in appropriate and useful flags along the way.
        
        @param output_file_name (Opt) A file name to assign to the new netlist
        @param name An internal name to assign to the netlist

        @throw CircuitError If the netlist was not created
        @return The file path of newly created netlist or an empty string if an error occured
        ''' 
        self._generateNetlist(output_file_name=output_file_name, name=name)
      
