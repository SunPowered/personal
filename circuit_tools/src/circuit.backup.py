'''
Created on 2012-07-04

@author: timvb
'''

import os
import re

import string

from utils import log
import component


_variable_flag = "$"
_variable_flag_re = r"\$"
_default_netlist_extension = ".cir"

#module errors
class CircuitError(Exception):
    '''
    Generic Circuit Error
    '''
    pass

class SchematicFileError(CircuitError):
    '''
    Schematic File Error
    '''
    pass

class SchematicParserError(CircuitError):
    '''
    Schematic Parser Error
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
    parseComponents() -- read the file and stores a list of components.  Also collects duplicate information
    isComponentUnique() -- checks whether component 
    --
    TODO: Methods to implement
    --
    verifyComponents(attribute_list) -- verify that all the components in the component list have the required attributes 
    printBOM(format) -- print the Bill Of Materials for the current component list 
    
    TODO: Add more doc
    '''


    def __init__(self, file_path, name=None, logger=None, required_attributes=None):
        '''
        Circuit Constructor
        
        @input: 
            filename - the file name of the circuit
            name(Opt) - a given name for the circuit
            required_attributes(Opt) - enforce all components have the given attributes
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
            raise SchematicFileError("file does not exist: %s"%(file_path))
        
        #Check .sch file type
        if os.path.splitext(file_path)[1] != ".sch":
            raise SchematicFileError("Given file must have a .sch extension")
        
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
        self.required_attributes = required_attributes
        self.component_list = component.SchematicComponentList()
        self.unique_components = component.BOMComponentList()
        self.restrictedDevices = ['INPUT', 'OUTPUT', 'NET']
        self.ignoreMultipleRefdes = True
        self._ignored = []
        
        
        #
        #Regex's
        #
        
        # Regex for a new component
        self.component_re = re.compile(r"^C(.*?)\n\{(.*?)\}", re.M|re.S)
        
        #Regex for an attribute within a component 
        self.attribute_re = re.compile(r"^(.+)=(.+)", re.M)
        
        #Regex for a variable value attribute
        self.schematic_variable_flag = _variable_flag
        self.variable_value_re = re.compile(r"^value="+_variable_flag_re+"(.+)", re.M)
        
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
    
    def getComponentList(self):
        return self.component_list
    
    def getUniqueComponents(self):
        return self.unique_components
    
    def getIgnored(self):
        return self._ignored
    
    def _readFileData(self):
        return open(self.getFilePath(), 'r').read()
    
    def _ignoreComponent(self, comp):
        '''
        Ignore a component
        '''
        self.logger.debug("Ignoring component: %s"%(comp))
        self._ignored.append(comp)
        
    def parseComponents(self):
        '''
        Parses schematic file.  
        
        Updates the list of Schematic Components and unique components
        '''
        
        
        if self.parseVariables():
            #Circuit contains variables, component parse cannot happen
            self.logger.error("variables detected in circuit %s, no component parse possible"%(self.getName()))
            raise SchematicParserError("Variables detected in Circuit %s.  Component parse aborted"%(self.getName()))
        
        self.logger.debug("Parsing %s"%(self.file_name))
        #open the file and read the data
        file_data = self._readFileData()
        
        #regex file data for all components
        components = self.component_re.findall(file_data)
        
        #check whether components were found
        if not components:
            raise SchematicParserError("Invalid regexp match")
        else:
            self.logger.debug("A total of %i components were found"%(len(components)))
        
        #handle components
        for component_ in components:
            header_data = component_[0]
            attribute_data = component_[1]
            symbol_file = header_data.split()[-1]
            
            #search for attributes wtihin component
            attributes  = self.attribute_re.findall(attribute_data)
            
            if not attributes:
                raise SchematicParserError("No attributes found for component: %s"%(symbol_file))
            
            #Create dictionary for component creation
            attributes = dict(attributes)
            
            #add symbol file to attributes
            attributes['symbol'] = symbol_file
            
            #Handle hierarchical symbols, traverse the sub circuit and parse that
            if 'source' in attributes.keys():
                #Hierarchical symbol, parse this and add to current component list
                tmp_circuit = Circuit(attributes['source'])
                tmp_circuit.parseComponents() 
                for comp in tmp_circuit.component_list:
                    self._addComponentToLists(comp)
                del tmp_circuit
            else:
                #Create component with the returned attributes
                comp = component.SchematicComponent(**attributes)
                if not comp.getAttribute('device') or not comp.getAttribute('refdes'):
                    self.logger.debug("component %s has no device or refdes attribute"%(comp.getAttribute('symbol')))
                    self._ignoreComponent(comp)
                    continue
                if (comp.getAttribute('device') in self.restrictedDevices):
                    self.logger.debug("component %s device () is restricted"%(comp, comp.getAttribute('device')))
                    self._ignoreComponent(comp)
                    continue
                
                #rename refdes for slotting
                if comp.hasAttribute('num_slots') and comp.hasAttribute('slot'):
                    '''
                    A slotted object is unique on the schematic level, yet shared with other slotted objects at a component level
                    '''
                    try:
                        num_slots = int(comp.getAttribute('num_slots'))
                        slot = int(comp.getAttribute('slot'))
                    except:
                        self.logger.error("Something funky with the slot or num_slot value on component: %s"%(comp))
                    
                    
                    if slot >= num_slots:
                        raise SchematicFileError("Component %s wants a slot (%i) larger than the num_slots attribute allows (%i)"%(comp, slot, num_slots))
                    self.logger.debug('Found slotted component %s. %i of %i'%(comp, slot, num_slots))
                    
                    #check whether component exists in component_list and unique_component_list
                    
                    
                    refdes = comp.getAttribute('refdes')+"."+str(comp.getAttribute('slot'))
                    comp.setAttribute('refdes', refdes)
                    del refdes
                    
                #Catch identical refdes components
                refdesMatches = self.component_list.find('refdes', comp.getAttribute('refdes'))
                if refdesMatches:
                    self.logger.warning('%i identical refdes match(es) found! %s'%(len(refdesMatches), comp.getAttribute('refdes')))
                    if self.ignoreMultipleRefdes:
                        #self._ignoreComponent(comp)
                        continue
                    #Identical refdes found, is num_slots defined
                
                    
                    
                
                #create components and attach to component list
                self._addComponentToLists(comp)
                del comp
            
        self.logger.info('Schematic parse returned %i valid components'%(len(self.component_list)))
        self.logger.info('Schematic parse ignored %i components'%(len(self.getIgnored())))
        
        #Sort list
        self.component_list.sort()
        self.unique_components.sort()

    def _isComponentUnique(self, comp):
        '''
        Checks a component agains the current component list
        '''
        return not (comp in self.component_list)
    
    def _addComponentToLists(self, comp):
        '''
        Adds a parsed component to the component lists and updates the unique component list
        '''
        unique = self._isComponentUnique(comp)
        
        if unique:
            #New component
            componentAttributes = comp.getAllAttributes()
            tmp_comp = component.BOMComponent(**componentAttributes)
            #tmp_comp.setAttribute('quantity', 1)
            self.unique_components.append(tmp_comp)
        else:
            #Update quantity 
            comp_index = self.unique_components.index(comp)
            tmp_comp = self.unique_components.pop(comp_index)
            tmp_comp.addAnother(refdes=comp.getAttribute('refdes'))
            self.unique_components.insert(comp_index, tmp_comp)
            #new_quantity = self.unique_components[comp_index].getAttribute('quantity') + 1
            #self.unique_components[comp_index].setAttribute('quantity', new_quantity)
            
        self.component_list.append(comp)
    
    def setRequiredAttributes(self, attributes, append=False):
        '''
        sets the required attributes, needed for verifying the components before a web parse or bom export
        
        '''
        self.required_attributes = attributes
    
    def _generateNetlist(self, type_, output_file_name=None, name=None):
        '''
        calls gnetlist automatically filling in appropriate and useful flags along the way.
        
        @inputs: 
            type: a str of the scheme model to parse with.  Defined in Netlist._enums["Types"]
                Accepted values:
                    "spice"
                    
            output_file_name: a str of the file name 
                    ...
        @outputs:
            file_path of new netlist, or None if an error occurred
            
        '''
        
        if not output_file_name:
            #create default from attributes
            output_file_name = self.getName() + _default_netlist_extension
        if os.path.splitext(output_file_name)[1] == "":
            #No extension on the output file name, add the default
            self.logger.info("No extension found on output file name: %s.  Adding default extension, %s"%(output_file_name, self.default_netlist_extension))
            output_file_name = output_file_name + self.default_netlist_extension
        
        #File goes in cwd
        output_file_path = os.path.join(os.getcwd(), output_file_name)    
        
        #Check types
        allowed_types = Netlist._enums["Types"]
        if type_ not in allowed_types.keys():
            raise CircuitError("Netlist type %s not allowed"%(type_))
        scm_type = allowed_types[type_][1]
        
        #Run gnetlist
        self.logger.info("Generating netlist of circuit %s"%(self.getName()))
        n = None
        
        try:
            os.system("gnetlist -g %s -o %s %s"%(scm_type, output_file_path, self.file_path))
        except:
            self.logger.error("Error occurred during netlist creation")
        else:
            if not os.path.isfile(output_file_path):
                raise NetlistError("Netlist file %s not created"(output_file_path))
            n = Netlist(output_file_path, name=self.getName(), logger=self.logger)
            
        return n
    
    def generateSpiceNetlist(self, **kwargs):
        '''
        generates a spice netlist 
        '''
        return self._generateNetlist("spice", **kwargs)
    
    def parseVariables(self):
        '''
        parses the file to see whether there are any variable values
        
        This is signified in the schematic by 
        value=$var
        
        regex ^value=\$(.+), re.M
        
        '''
        
        #Parse variables from given file path using regex
        try:
            variables = self.variable_value_re.findall(self._readFileData())
        except:
            return None
        
        self.variables = variables
        self.variables.sort()                                          
        return self.variables

      
class NetlistError(CircuitError):
    pass

class Netlist(object):
    '''
    Netlist object, required for simulations and much more
    
    @input:
        file_path - The file path of the current netlist
        name (Optional) - Assign a name to the netlist
        
    TODO: Implement a removal of any .INCLUDE .*.LIB statements from netlist
    '''   
    
    _default_type = "spice"
    _enums = {"Types":{"spice":[0, 'spice-sdb']}}
    
    def __init__(self, file_path, name=None, logger=None, type_=None):
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
        if not os.path.isfile(os.path.normpath(file_path)):
            raise NetlistError("File does not exist")
        
        #Template
        self.template = string.Template(open(self.file_path, 'r').read())   
        
        #temp file_path
        path, ext = os.path.splitext(self.file_path)
        self.temp_file_path = path + '.tmp' + ext
        self.temp_file_name = os.path.split(self.temp_file_path)[1]
        
        
        #type init
        if not type_:
            self.setType(self._default_type)
        else:
            self.setType(type_)    
            
        
        #Regex
        self.comment_re = r"\*"
        self.variable_re = re.compile(r"^[^"+self.comment_re+r"].*" + _variable_flag_re + r"(\w+)", re.M)
        
        self.variables = []
            
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
    def getType(self):
        return self.type_
    
    def setType(self, type_):
        if not type_ in self._enums["Types"].keys():
            return None
        self.type_ = type_
        
    def getTemplate(self):
        return self.template
    
    def getFilePath(self):
        return self.file_path
    
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
        
    def setVariables(self, variables):
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
    
    def removeNetlistFile(self):
        '''
        removes the current file.  useful for cleanup operations after a batch process
        '''
        self.logger.debug("Removing file %s"%(self.file_path))
        return os.remove(self.file_path)
      
if __name__ == "__main__":
    import pprint
    
    C1 = Circuit("../data/schmitt.trigger.sch")
    C1.parseComponents()
    pprint.pprint( C1.component_list )
    pprint.pprint( C1.unique_components )