'''
@package bom.circuit
@file bom/circuit.py
@author: timvb
@brief Module containing the BOMCircuit.  Useful for output of schematic components
'''
import re

import prettytable

from utils import log, config
from schematic.circuit import Circuit, CircuitError, CircuitFileError
from bom.component import BOMComponent, BOMComponentList, BOMComponentError

class BOMCircuitError(Exception):
    pass

class BOMCircuitParserError(BOMCircuitError):
    '''
    Schematic Parser Error
    '''
    pass

class BOMCircuitParserComponentError(BOMCircuitParserError):
    pass
class BOMCircuit(Circuit):
    '''
    @class bom.circuit.BOMCircuit
    @brief Ability to parse components, fetch info from web API, print out reports
    '''
    
    _flagged_devices = config.BOM_PARSE_MODEL["FLAGGED_DEVICES"]
    
    def __init__(self, *args, **kwargs):
        '''
        @brief BOMCircuit constructor class
        @param args from  schematic.circuit.Circuit
        @param kwargs @li required_attributes (Opt) A list of mandatory attributes for each 
        component
        '''
        logger = kwargs.get('logger', None)
        if not logger:
            kwargs['logger'] = log.getDefaultLogger('bom.circuit.BOMCircuit')
            
        Circuit.__init__(self, *args, **kwargs)
        
        self.required_attributes = kwargs.get('required_attributes', None)
        
        self.component_list = BOMComponentList()
        #self.unique_components = BOMComponentList()
        
        #self.ignoreMultipleRefdes = True
        #self._ignored = []

        # Regex for a new component
        self.component_re = re.compile(r"^C(.*?)\n\{(.*?)\}", re.M|re.S)
        
        #Regex for an attribute within a component 
        self.attribute_re = re.compile(r"^(.+)=(.+)", re.M)
        
        #Try to parse if file path was given
        if self.getFileName():
            try:
                self.parseComponents()
            except BOMCircuitParserError, msg:
                self.logger.error("There was a parsing error during BOMCircuit init.  Ignoring")
    
    def __contains__(self, comp):
        '''
        @brief contains override
        '''    
        return comp in self.component_list
    #def setRequiredAttributes(self, attributes, append=False):
    #    '''
    #    sets the required attributes, needed for verifying the components before a web parse or bom export
    #    
    #    '''
    #    self.required_attributes = attributes        
        
    def getComponentList(self):
        '''
        @brief returns the current component list
        '''
        return self.component_list
    
    #def getUniqueComponents(self):
        
    #    return self.unique_components
    
    #def getIgnored(self):
    #    return self._ignored
    
    #def _ignoreComponent(self, comp):
    #    '''
    #    Ignore a component
    #    '''
    #    #self.logger.debug("Ignoring component: %s"%(comp))
    #    #self._ignored.append(comp)
    #    pass
    
    def parseComponents(self):
        '''
        @brief Parses schematic file for a BOM Export  
        @return a component list object
        @throw bom.circuit.BOMCircuitParserError If there was an error during a regex match
        @throw bom.circuit.BOMCircuitParserComponentError  If there is an error during BOMComponent instantiation
        @details
        Steps.
        1.    read circuit file data, and use regex to separate all component blocks
        2.    for each component
            3.Split the header line, get symbol from this
            4. From rest, parse for attribute=value matches
            5. If attribute source exists, it is a hierarchical symbol, parse recursively
            6. Sort out flagged attributes, ignore component if flagged
            7.  Sort out flagged devices, ignore flagged components
            ...
            8. Create a new BOM Component
            9.  Add to component lists
        
        Updates the list of Schematic Components and unique components
        '''
        
        
        #if self.parseVariables():
        #    #Circuit contains variables, component parse cannot happen
        #    self.logger.error("variables detected in circuit %s, no component parse possible"%(self.getName()))
        #    raise CircuitParserError("Variables detected in Circuit %s.  Component parse aborted"%(self.getName()))
        
        self.logger.debug("Parsing %s"%(self.file_name))
        #open the file and read the data
        file_data = self._readFileData()
        
        #regex file data for all components
        components = self.component_re.findall(file_data)
        
        #check whether components were found
        if not components:
            self.logger.error("There was an error parsing the circuit during the regex match. Aborting parse")
            raise BOMCircuitParserError("There was an error parsing the circuit during the regex match. Aborting parse")
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
                raise BOMCircuitParserError("No attributes found for component: %s"%(symbol_file))
            
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
                
                if not 'refdes' in attributes.keys():
                    self.logger.debug("component %s has no refdes attribute"%(attributes['symbol']))
                    #self._ignoreComponent(comp)
                    continue
                
                if not 'device' in attributes.keys():
                    self.logger.debug("component %s has no device attribute"%(attributes['symbol']))
                    #self._ignoreComponent(comp)
                    continue
                
                if attributes['device'] in self._flagged_devices:
                    self.logger.debug("component %s device (%s) is restricted"%(attributes['symbol'], attributes['device']))
                    #self._ignoreComponent(comp)
                    continue
                
                
                
                #rename refdes for slotting
                if 'num-slots' in attributes.keys():
                    #attribute num slots exists
                    num_slots = int(attributes['num-slots'])
                    if num_slots > 0:
                        #num-slots is greater than 0, slotting should be enabled
                        if 'slot' in attributes.keys():
                            #slots also defined
                            slot = int(attributes['slot'])
                            if slot < 1 or slot > num_slots:
                                raise CircuitParserError("Strange Slotting attributes.  slot: %i, num_slots: %i"%(slot, num_slots))
                            '''
                            A slotted object is unique on the schematic level, yet shared with other slotted objects at a component level
                            '''

                            self.logger.debug('Found slotted component %s. %i of %i'%(comp, slot, num_slots))
                            
                            #check whether component exists in component_list and unique_component_list
                            
                            
                            refdes = attributes['refdes']+"."+str(attributes['slot'])
                            attributes['refdes'] = refdes
                            
                    
                #Catch identical refdes components
                #refdesMatches = self.component_list.find('refdes', attributes['refdes'])
                #if refdesMatches:
                #    self.logger.warning('%i identical refdes match(es) found! %s'%(len(refdesMatches), attributes['refdes']))
                    #if self.ignoreMultipleRefdes:
                        #self._ignoreComponent(comp)
                    #    continue
                    #Identical refdes found, is num_slots defined
                
                    
                #Create component with the returned attributes
                try:
                    comp = BOMComponent(**attributes)    
                except BOMComponentError, msg:
                    raise BOMCircuitParserComponentError("Error creating BOM component: %s"%(msg))
                
                #attach to component list
                self.component_list.append(comp)
                del comp
            
        self.logger.info('Schematic parse returned %i valid components'%(len(self.component_list)))
        #self.logger.info('Schematic parse ignored %i components'%(len(self.getIgnored())))
        
        #Sort list
        self.component_list.sort()
        #self.unique_components.sort()
        return self.getComponentList()

    def _isComponentUnique(self, comp):
        '''
        @brief Checks a component agains the current component list
        @return bool
        '''
        return not (comp in self.component_list)
    
    def printComponentsToFile(self, file_name=None):
        '''
        For now, just print the required attributes of the components, plus the refdes
        
        Should be sorted by device, then by value, then by manufacturer
        
        Output format is currently tab delimited
        @todo implement a better templating mechanism
        '''
        required_attributes = config.bom_config.BOM_PARSE_MODEL["REQUIRED_ATTRIBUTES"]
        
        if not file_name:
            circuit_name = self.getName()
            if not circuit_name:
                file_name = config.bom_config.DEFAULT_BOM_NAME + config.bom_config.BOM_EXTENSION
            else:
                file_name = circuit_name + config.bom_config.BOM_EXTENSION
        
        #open file for writing
        try:
            f = open(file_name, 'w')
        except Exception, msg:
            raise BOMCircuitError("Error opening File to write: %s.  Failed with message: %s"%(file_name, msg))
        
        
        #print header
        header = "Qty."
        header += "\t"
        for attr in required_attributes:
            #reformat for printing
            attr = " ".join(attr.split("_"))
            

        
            header += attr
            header += "\t"
        header += "\n"
        
        f.write(header)
        
        #Print components
        for component in self.getComponentList():
            line = ""
            line += "%i"%(component.getQuantity())
            line += "\t"
            for attr in required_attributes:
                
                line += component.getAttribute(attr) or "\t"
                line += "\t"
                
            line += "\n"
            
            f.write(line)
            
        f.close()
        
    def printComponentsToFile2(self, file_name=None):
        '''
        Using the prettytable library
        '''
        required_attributes = config.bom_config.BOM_PARSE_MODEL["REQUIRED_ATTRIBUTES"]
        
        if not file_name:
            circuit_name = self.getName()
            if not circuit_name:
                file_name = config.bom_config.DEFAULT_BOM_NAME + config.bom_config.BOM_EXTENSION
            else:
                file_name = circuit_name + config.bom_config.BOM_EXTENSION
                
        fields = ["Quantity"]
        for attr in required_attributes:
            attr = " ".join(attr.split("_"))
            fields.append(attr.capitalize())
            
        table = prettytable.PrettyTable(fields)
        #table.set_field_align("Quantity", 'l')
        table.set_style(prettytable.PLAIN_COLUMNS)
        
        for component in self.getComponentList():
            line = [component.getQuantity()]
            for attr in required_attributes:
                line.append(component.getAttribute(attr))
                
            table.add_row(line)
            
        open(file_name, 'w').write(str(table))
        