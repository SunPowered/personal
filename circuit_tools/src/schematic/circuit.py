'''
Created on 2012-07-04

@author: timvb
'''

import os
#import re

#import string

from utils import log, config, fs
#import schematic.component as component
from schematic.netlist import Netlist


#_variable_flag = "$"
#_variable_flag_re = r"\$"


#module errors
class CircuitError(Exception):
    '''
    Generic Circuit Error
    '''
    pass

class CircuitFileError(CircuitError):
    '''
    Schematic File Error
    '''
    pass



class Circuit(object):
    '''
    Circuit object.  Represents a schematic circuit.  Able to parse gschem schematic file.
    
    Currently intended only as a post processor to gschem.
    
    --
    The following methods are available:
    --
    setName(), getName()
    getFilePath(), getFileName()
    
    These will be moved to ComponentCircuit subclass
    parseComponents() -- read the file and stores a list of components.  Also collects duplicate information
    isComponentUnique() -- checks whether component 
    --
    TODO: Methods to implement
    --
    verifyComponents(attribute_list) -- verify that all the components in the component list have the required attributes 
    printBOM(format) -- print the Bill Of Materials for the current component list 
    
    TODO: Add more doc
    '''


    def __init__(self, file_path, name=None, logger=None):
        '''
        Circuit Constructor
        
        @input: 
            filename - the file name of the circuit
            name(Opt) - a given name for the circuit
            
        @output: None
        
        Creates an internal component and unique_component list for easy BOM generation
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
        if not name:
            self.name = os.path.splitext(self.file_name)[0]
            self.logger.debug('assigned automatic name to circuit: %s'%(self.getName()))
        else:
            self.name = name
        #self.required_attributes = required_attributes

        self.netlist_cls = Netlist
        
        
        #
        #Regex's
        #
        

        

        
        #Netlist attributes
        #self.default_netlist_extension = ".net"
        
        #self.parser = SchematicParser(self.filename)
        #self.logger.debug('Created Circuit: %s'%(self.getName()))
    
    def setName(self, name):
        '''
        sets the circuit name
        '''
        self.name=name    
        
    def getName(self):
        '''
        gets the circuit name
        '''
        return self.name
    
    def getFileName(self):
        return self.file_name
    
    def getFilePath(self):
        return self.file_path
    

    
    def _readFileData(self):
        return open(self.getFilePath(), 'r').read()
    

    

    
    def _generateNetlist(self, output_file_name=None, name=None):
        
        #import netlist
        '''
        calls gnetlist automatically filling in appropriate and useful flags along the way.
        
        @inputs: 
            netlist_scheme: a str of the scheme model to parse withh
                Accepted values:
                    "spice-sdb"
                    ...
            
                    
            output_file_name: a netlist object 
                    ...
        @outputs:
            file_path of new netlist, or None if an error occurred
            
        '''
        
        if not output_file_name:
            #create default from attributes
            output_file_name = self.getName() + config.DEFAULT_NETLIST_EXTENSION
        if os.path.splitext(output_file_name)[1] == "":
            #No extension on the output file name, add the default
            self.logger.info("No extension found on output file name: %s.  Adding default extension, %s"%(output_file_name, self.default_netlist_extension))
            output_file_name = output_file_name + self.default_netlist_extension
        
        #File goes in same directory as this circuit
        #change the cwd to the circuit directory, to help with relative paths in schematics
        old_working_directory = os.getcwd()
        new_working_directory = fs.switchWDFromFilePath(self.getFilePath())
        
        output_file_path = os.path.join(new_working_directory, output_file_name)    
        
        #Check types
        #allowed_types = netlist.Netlist._enums["Types"]
        #if type_ not in allowed_types.keys():
        #    raise CircuitError("Netlist type %s not allowed"%(type_))
        scm_type = self.netlist_cls._netlist_scheme
        

        #Run gnetlist
        self.logger.info("Generating netlist of circuit %s"%(self.getName()))
        n = None
        
        try:
            os.system("gnetlist -g %s -o %s %s"%(scm_type, output_file_path, self.file_path))
        except:
            self.logger.error("Error occurred during netlist creation")
        else:
            if not os.path.isfile(output_file_path):
                raise CircuitError("Netlist file %s not created"%(output_file_path))
            n = self.netlist_cls(output_file_path, name=self.getName(), logger=self.logger)
        finally:
            #No matter what, change back to the old original directory
            os.chdir(old_working_directory)   
            
        return n
    

    


      
        
if __name__ == "__main__":
    import pprint
    
    C1 = Circuit("../data/schmitt.trigger.sch")
    C1.parseComponents()
    pprint.pprint( C1.component_list )
    pprint.pprint( C1.unique_components )