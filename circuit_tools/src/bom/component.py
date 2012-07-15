'''
@package bom.component
@file bom/component.py
@author: timvb
@brief Contains the Bill of Materials Component object
'''
from utils import config
from schematic.component import Component, ComponentError, ComponentList, ComponentListError 

class BOMComponentError(ComponentError):
    pass



class BOMComponent(Component):
    '''
    @brief A Bill Of Materials Component.
    @details
    Differences from a Schematic Component is that multiple quantities are allowed.  
    Required attributes are determined in the utils.config.BOM_PARSE_MODEL object
    '''
    
    _required_attributes = config.BOM_PARSE_MODEL["REQUIRED_ATTRIBUTES"]
    _ignored_attributes = config.BOM_PARSE_MODEL["IGNORED_ATTRIBUTES"]
    
    def __init__(self, **kwargs):
        '''
        @brief BOM Component constructor method
        @param kwargs A collection of attribute value pairs to be saved to the component
        '''        
        [kwargs.__setitem__(attr, None) for attr in self._required_attributes if attr not in kwargs.keys()]
        Component.__init__(self, **kwargs)
        self.quantity = 1
        
        #self._ignore_attrs = ["quantity"]
    def __repr__(self):
        '''
        @brief repr override
        @todo Only print required attributes
        '''
        return "%s[%s][%s - %s](%i)"%(str(self.device), str(self.value), str(self.manufacturer), str(self.part_number), self.quantity)
    
    def addAnother(self):
        '''
        @brief Increase the quantity by one
        '''
        self.quantity += 1
        
    '''
    def setAttribute(self, attribute, value):
        if attribute == "refdes":
            self.refdes.append(value)
            return
        super(BOMComponent, self).setAttribute(attribute, value)
    '''
    def getQuantity(self):
        '''
        @brief return the current quantity
        @return int
        '''
        return self.quantity
    

                
class BOMComponentList(ComponentList):
    '''
    @brief An object for storing a list of BOM components
    '''
    
    
    def append(self, obj):
        if isinstance(obj, self.element_obj):
            index = self.findIndex(obj)
            if index:
                self.elements[index[0]].addAnother()
            else:
                self.elements.append(obj)  
            
    def sort(self, attribute='device'):
        return super(BOMComponentList, self).sort(attribute=attribute)