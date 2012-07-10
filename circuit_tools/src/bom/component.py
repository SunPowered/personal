'''
Created on 2012-07-08

@author: timvb
'''
from utils import config
from schematic.component import Component, ComponentError, ComponentList, ComponentListError 

class BOMComponentError(ComponentError):
    pass



class BOMComponent(Component):
    '''
    A Bill Of Materials Component.
    
    Differences from a Schematic Component is that multiple quantities are allowed.  
    
    Unique attributes are manufacturer and part-number and device
    '''
    
    _required_attributes = config.BOM_PARSE_MODEL["REQUIRED_ATTRIBUTES"]
    _ignored_attributes = config.BOM_PARSE_MODEL["IGNORED_ATTRIBUTES"]
    
    def __init__(self, **kwargs):
        
        
        [kwargs.__setitem__(attr, None) for attr in self._required_attributes if attr not in kwargs.keys()]
        Component.__init__(self, **kwargs)
        self.quantity = 1
        
        #self._ignore_attrs = ["quantity"]
    def __repr__(self):
        
        return "%s[%s - %s][%i]"%(str(self.device), str(self.manufacturer), str(self.part_number), self.quantity)
    
    def addAnother(self, refdes=None):
        self.quantity += 1
        if refdes:
            self.setAttribute('refdes', refdes)
    '''
    def setAttribute(self, attribute, value):
        if attribute == "refdes":
            self.refdes.append(value)
            return
        super(BOMComponent, self).setAttribute(attribute, value)
    '''
    def getQuantity(self):
        return self.quantity
    

                
class BOMComponentList(ComponentList):
    
    
    
    def append(self, obj):
        if isinstance(obj, self.element_obj):
            index = self.findIndex(obj)
            if index:
                self.elements[index[0]].addAnother()
            else:
                self.elements.append(obj)  
            
    def sort(self, attribute='device'):
        return super(BOMComponentList, self).sort(attribute=attribute)