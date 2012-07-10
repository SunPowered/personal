'''
Created on 2012-07-04

@author: timvb
'''

import re

from utils import log

class ComponentError(Exception):
    pass

class Component(object):
    '''
    Base component class.  To be inherited by higher level component objects 
    
    Keeps track of all component attributes
    
    Provides the following methods:
    
    Component.hasAttribute(attribute)            -    Checks whether the object has the given attribute. Returns Boolean
    Component.getAttribute(attribute)            -    Returns the value of the stored attribute, None otherwise
    Component.setAttribute(attribute, value)    -    Sets a given attribute to a given value
    Component.getAttributes()                    -    Returns a list of all component attributes
    Component.getAllAttributesAsDict()            -   Returns a dict object containing the attributes and their values as key, item pais 
    '''
    _required_attributes = ['refdes']
    
    def __init__(self, logger=None, **kwargs):
        #Logging
        if not logger:
            self.logger = log.getDefaultLogger('schematic.component.Component')
        else:
            self.logger = logger
        
        #Ignore Required Attributes for now
        #try:
        #    for attr in self.required_attrs:
        #        if attr not in kwargs.keys():
        #            kwargs[attr] = None
        #except:
        #    self.required_attrs = []
        
        #if not unique_attributes:
        #    self.unique_attributes = []
        #else:
        #    self.unique_attributes = unique_attributes
            
        self.attributes = []
        [self.setAttribute(attr, value) for attr, value in kwargs.items()]
        self._ignored_attributes = []
    
    def __eq__(self, b):
        '''
        compares only the required attributes upon ==
        '''
        result = True
        for attr in self._required_attributes:
            
            attr1 = self.getAttribute(attr)
            attr2 = b.getAttribute(attr)
            
            result = (result and attr1 == attr2) 
            if not result:
                return result            
        return result
    
    def hasAttribute(self, attribute):
        #return self.getAttribute(attribute)
        return attribute in self.getAttributes()
            
        
    def getAttribute(self, attribute):
        '''
        Returns the attribute value if it exists, None otherwise
        '''
        if attribute in self.attributes:
            return self.__getattribute__(attribute)
        else:
            return None
        
    def setAttribute(self, attribute, value):
        '''
        Set a new component attribute
        '''
        
        #Check whether attribute is in the ignored attribute list
        if attribute in self._ignored_attributes:
            return
        
        attribute = str(attribute).replace("-","_")
        
        #Check whether attribute already exists
        if self.hasAttribute(attribute):
            #What to do?
            #I guess, make it a list and start appending
            current_value = self.getAttribute(attribute)
            if isinstance(current_value, list):
                self.__setattr__(attribute, current_value.append(value))
            else:
                #Single value exists, make it into a list
                self.__setattr__(attribute, [current_value, value])
        
        else:
            self.__setattr__(attribute, value)
            self.attributes.append(attribute)
        
        
    
    def getAttributes(self):
        '''
        Return all attributes
        '''
        return self.attributes 
    
    def getAllAttributesAsDict(self):
        '''
        Return all the attributes and values in a dict format.  
        
        Useful for copying a component to a dummy object.  i.e. 
    
        >>>attributes  = {attribute_1:value_1, attribute_2:value_2}
        >>>c = Component(attributes)
        >>>new_c = Component(c.getAllAttributes())
        >>>new_c.getAttribute(attribute_1)
        value_1
        >>>
        '''
        d = {}
        for attr in self.getAttributes():
            d[attr] = self.getAttribute(attr)
        return d   
    

class ComponentListError(Exception):
    pass
        
class ComponentList(object):
    
    def __init__(self, iterable=None, name=None):
        self.elements = lst = []
        if iterable:
            for value in iterable:
                lst.append(value)
        self.elements = lst
        self.name = name  
        self.element_obj = Component   
    
    def __str__(self):
        import pprint
        return pprint.pprint(self.elements)      
    def __contains__(self,y):
        return self.elements.__contains__(y)
    
    def __iter__(self):
        
        return self.elements.__iter__()
    
    def __len__(self):
        return self.elements.__len__()
    
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
    
    def append(self, obj):
        '''
        No duplicate items allowed 
        '''
        found_index = self.findIndex(obj)
        if found_index:
            raise ComponentListError("Element with attributes already exist in list.  %s Cannot append"%(str(obj)))
        return self.elements.append(obj)
    
    def find(self, attribute, value):
        '''
        Returns all components matching the attribute value given
        '''
        c = ComponentList()
        for component in filter(lambda component: component.getAttribute(attribute)==value, self):
            c.append(component)
            
        return c
    
    def findIndex(self, comp):
        '''
        Search for a given component in the stored elements, return a list of matching indices
        '''
        return [i for i, component in enumerate(self.elements) if component == comp]
        
    def findAndPop(self, attribute, value):
        '''
        Similar to find() but removes the matching entries from the list
        '''
        matches = self.find(attribute, value)
        for match in matches:
            self.remove(match)
        return matches  
     
    def sort(self, attribute=None):
        '''
        Sort the list alphanumerically by a given attribute.  All children must override this with the attribute keyword set
        '''
        def chunkify(s):
            '''return a list of numbers and non-numeric substrings of +str+
        
            the numeric substrings are converted to integer, non-numeric are left as is
            '''
            chunks = re.findall("(\d+|\D+)",s)
            chunks = [re.match('\d',x) and int(x) or x for x in chunks] #convert numeric strings to numbers
            return chunks   
                 
        def sortAttr(a, b):
            chunka = chunkify(a.getAttribute(attribute))
            chunkb = chunkify(b.getAttribute(attribute))
            
            return cmp(chunka, chunkb)
        
        
        return self.elements.sort(sortAttr)    
    
"""        
class ComponentList(list):
    '''
    Base class for a component List.
    
    Inherits from a basic list.
    
    Overrides 
    '''
    def append(self, obj):
        
        #Components must be unique, as given by the _required_attributes attribute of the Component class
        if isinstance(obj, Component):
            if obj in self:
                #component is not unique
                return
            
            super(ComponentList, self).append(obj)
    
       
    
    def find(self, attribute, value):
        '''
        Returns all components matching the attribute value given
        '''
        c = ComponentList()
        for component in filter(lambda component: component.getAttribute(attribute)==value, self):
            c.append(component)
            
        return c
    
    def findAndPop(self, attribute, value):
        '''
        Similar to find() but removes the matching entries from the list
        '''
        matches = self.find(attribute, value)
        for match in matches:
            self.remove(match)
        return matches   
    def sort(self, attribute=None):
        '''
        Sort the list alphanumerically by a given attribute.  All children must override this with the attribute keyword set
        '''
        def chunkify(s):
            '''return a list of numbers and non-numeric substrings of +str+
        
            the numeric substrings are converted to integer, non-numeric are left as is
            '''
            chunks = re.findall("(\d+|\D+)",s)
            chunks = [re.match('\d',x) and int(x) or x for x in chunks] #convert numeric strings to numbers
            return chunks   
                 
        def sortAttr(a, b):
            chunka = chunkify(a.getAttribute(attribute))
            chunkb = chunkify(b.getAttribute(attribute))
            
            return cmp(chunka, chunkb)
        
        
        super(ComponentList, self).sort(sortAttr)

class SchematicComponent(Component):
    '''
    A base object for a schematic component.  
    '''
    
    def __init__(self, **kwargs):
        '''
        kwargs are intended to be component attribute value pairs

        '''
        #Mandatory attributes
        self.required_attrs = ['refdes', 'value', 'device','symbol']
        Component.__init__(self, **kwargs)
        self._ignore_attributes.append('refdes')
        
        #No vendor support yet                
        #self.parseVendor=False
        #self.vendor = kwargs.get('vendor')     
        
        

    
    def __eq__ (self, y):
        if type(y) != type(self):
            raise TypeError("Comparing object must be of same type")
        eq = True
        
        
        #attrx = self.attributes.remove('refdes')
        #attry = y.attributes.remove('refdes')
        
        for attr in self.attributes:
            if attr == "refdes":
                continue
            if self.getAttribute(attr) != y.getAttribute(attr):
                eq = False
                break
        
        return eq
     
    def __repr__(self):
        return str(self.refdes)+"["+str(self.value)+"]"

        
    def setAttribute(self, attribute, value):
        '''
        Set a new component attribute
        '''
        #Split any periods in the refdes, indicates a slotted component, i.e. U1.1, U1.2, would all be saved under U1
        if attribute == "refdes":
            try:
                value = value.split('.')[0]
            except:
                #Ignore an error that can be caused when nothing is set for refdes
                pass
        super(SchematicComponent, self).setAttribute(attribute, value)
        #self.__setattr__(attribute, value)
        #self.attributes.append(attribute)
        
    
    def parseFromVendor(self, vendor):
        '''
        parses information from the vendor.  
        
        Requires various attributes to be set, as defined by the vendor being parsed
        Vendor is a custom object with required attributes and a parse function available
        '''
        
     
    def addVendorInfo(self):
        '''
        old.  use parseFromVendor
        '''
        vendor = self.getAttribute('vendor')
        vendor_number = self.getAttribute('vendor-number')
        if (not vendor) or (not vendor_number):
            return None
        
        if vendor == 'Digikey':
            parser = vendors.digikey.DigikeyVendorParser()
            
        vendor_component = parser.parse(vendor_number)
        
        if not vendor_component:
            return None
        
        for attribute in self.attributes:
            vendor_attribute = vendor_component.__getattribute__(attribute)
            if vendor_attribute:
                self.setAttribute(attribute, vendor_attribute)
        
    
            
class SchematicComponentList(ComponentList):
    '''
    Schematic Component List.  A custom list for components
    '''

    def sort(self, attribute='refdes'):

        super(SchematicComponentList, self).sort(attribute=attribute)
        
 """ 
        
if __name__ == "__main__":
    pass
    