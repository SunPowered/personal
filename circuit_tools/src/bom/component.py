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
        try:
            return "%s[%s][%s - %s](%i)"%(str(self.device), str(self.value), str(self.manufacturer), str(self.part_number), self.quantity)
        except:
            return ""
    def addAnother(self, obj=None):
        '''
        @brief Increase the quantity by one
        @details  If an object is given as an argument, all non-required attributes will be 
        appended to the present value.  This serves to keep all unique attributes as they are yet keep 
        track of variations in non-unique attributes.  
        e.g. A Panasonic 1K 0603 resistor is used several times in a design.  The part itself is 
        identified by its unique attributes, yet the refdes of each instance in the circuit is tracked
        for printing later
        '''
        self.quantity += 1
        if obj:
            for attr in obj.getAttributes():
                if attr not in self._required_attributes:
                    
                    value = self.getAttribute(attr)
                    
                    if isinstance(value, list):
                        if obj.getAttribute(attr) not in value: 
                            value.append(obj.getAttribute(attr))
                    else:
                        if obj.getAttribute(attr) != value:
                            setattr(self, attr, [value, obj.getAttribute(attr)])
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
    element_obj = BOMComponent
    
    @property
    def total_number_parts(self, *args):
        '''
        @brief Returns the total part count for the list
        @param args (Opt) Use this to specifiy a criteria to select.  Use a attribute, value
        pair for the *args tuple
        '''
        if args:
            try:
                attribute, value = args
            except:
                raise BOMComponentError("If arguments are to be provdided, they must be in a attribute, value pair")
            else:
                return sum([x.getQuantity() for x in self.find(attribute, value)])
            
        return sum([x.getQuantity() for x in self])  
    
    @property
    def total_unique_parts(self):
        '''
        @brief returns the total unique part count for the list
        '''
        return len(self) 
      
    def append(self, obj):
        if isinstance(obj, self.element_obj):
            index = self.findIndexByComponent(obj)
            if index:
                self[index[0]].addAnother(obj)
            else:
                list.append(self, obj)  
            
    def sort(self, attribute='device'):
        return super(BOMComponentList, self).sort(attribute=attribute)