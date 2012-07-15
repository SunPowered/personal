'''
@file schematic/component.py
@package schematic.component

@author timvb
@brief A module containing schematic component objects
@version 0.1.0
@details
This holds the general Component object and ComponentList object.  Useful for
simple circuit checks, and as a base class for more specific applications
'''

import re

from utils import log

class ComponentError(Exception):
    pass

class Component(object):
    '''
    @brief General schematic component class.  To be inherited by higher level component objects      
    '''
    _required_attributes = ['refdes']
    
    def __init__(self, logger=None, **kwargs):
        '''
        @brief Component Constructor
        @param logger (Opt) Custom logging object
        @param **kwargs Keywords defined by (attribute, value) key value pairs
        
        Any attributes set using key word arguments will be saved in a local list
        of custom arguments.
        '''
        #Logging
        if not logger:
            self.logger = log.getDefaultLogger('schematic.component.Component')
        else:
            self.logger = logger
            
        self.attributes = []
        [self.setAttribute(attr, value) for attr, value in kwargs.items()]
        #self._ignored_attributes = []
    
    def __eq__(self, b):
        '''
        @brief compares only the custom attributes upon an __eq__ call
        @param b the object to compare
        '''
        result = True
        for attr in self.getAttributes():
            
            attr1 = self.getAttribute(attr)
            attr2 = b.getAttribute(attr)
            
            result = (result and attr1 == attr2) 
            
            #Break at first false equality 
            if not result:
                return result            
        
        #Should be true if we got this far    
        return result
    
    def hasAttribute(self, attribute):
        '''
        @brief Checks whether this component has a given attribute
        @return boolean
        '''
        return attribute in self.getAttributes()
            
        
    def getAttribute(self, attribute):
        '''
        @brief A method to return a given attribute
        @return the attribute value if it exists, [] otherwise
        '''
        if attribute in self.attributes:
            return self.__getattribute__(attribute)
        else:
            return []
        
    def setAttribute(self, attribute, value):
        '''
        @brief Set a new component attribute to a value
        
        Replaces any schematic friendly "-" character with a python friendly "_" \n
        If attribute already exists, either create a list of the old and new attribute
        or append it to the existing list
        '''
        
        
        attribute = str(attribute).replace("-","_")
        
        #Check whether attribute already exists
        if self.hasAttribute(attribute):
            #Make it a list and start appending
            current_value = self.getAttribute(attribute)
            
            #Try statement is a bit more elegant
            try:
                current_value.append(value)
            except AttributeError:
                #single_attribute, make a list
                current_value = [current_value, value]
            else:
                self.__setattr__(attribute, current_value)
            '''    
            if isinstance(current_value, list):
                self.__setattr__(attribute, current_value.append(value))
            else:
                #Single value exists, make it into a list
                self.__setattr__(attribute, [current_value, value])
            '''
        else:
            #Attribute does not already exist, 
            self.__setattr__(attribute, value)
            self.attributes.append(attribute)
        
        
    
    def getAttributes(self):
        '''
        @brief Return all attributes
        @return a list of all attributes
        '''
        return self.attributes 
    
    def getAllAttributesAsDict(self):
        '''
        @brief Return all the attributes and values in a dict format.  
        @return a dict of all attribute,value key value pairs
        
        Useful for copying a component to a dummy object.  i.e. 
        @code
        >>>attributes  = {attribute_1:value_1, attribute_2:value_2}
        >>>c = Component(attributes)
        >>>new_c = Component(c.getAllAttributes())
        >>>new_c.getAttribute(attribute_1)
        value_1
        @endcode
        '''
        d = {}
        for attr in self.getAttributes():
            d[attr] = self.getAttribute(attr)
        return d   
    

class ComponentListError(Exception):
    pass
        
class ComponentList(object):
    '''
    @brief An object for storing and sorting Components
    '''
    def __init__(self, iterable=None, name=None):
        '''
        @brief ComponentList Constructor
        @param iterable (Opt) An initial list to parse into storage
        @param name (Opt) A name to assign to the component list
        '''
        self.elements = []

        self.name = name  
        self.element_obj = Component   
    
        if iterable:
            for value in iterable:
                self.elements.append(value)
        
    def __repr__(self):
        '''
        @brief __repr__ override
        '''
        #import pprint
        #pprint.pprint(self.elements)
        return str(self.elements)
              
    def __contains__(self,y):
        '''
        @brief __contains__ override
        @param y object to pass to contains
        ''' 
        return self.elements.__contains__(y)
    
    def __iter__(self):
        '''
        @brief iterate over the list
        '''
        return self.elements.__iter__()
    
    def __len__(self):
        '''
        @brief __len__ override
        '''
        return self.elements.__len__()
    
    def setName(self, name):
        '''
        @brief Sets the name of the component list
        @param name The name to assign to the component list
        '''
        self.name = name
        
    def getName(self):
        '''
        @brief Return the current name of the list
        @return A string object
        '''
        return self.name
    
    def append(self, obj):
        '''
        @brief Append a new Component to the list
        @param obj A Component to append
        @throw schematic.component.ComponentListError When a component already exists in the list, as determined by findIndex() 
        '''
        found_index = self.findIndex(obj)
        if found_index:
            raise ComponentListError("Element with attributes already exist in list.  %s Cannot append"%(str(obj)))
        return self.elements.append(obj)
    
    def find(self, attribute, value):
        '''
        @brief Finds all components matching the attribute value provided
        @param attribute The attribute to find
        @param value The value of the attribute to find
        @return a component list of the matched objects
        '''
        c = ComponentList()
        for component in filter(lambda component: component.getAttribute(attribute)==value, self):
            c.append(component)
            
        return c
    
    def findIndex(self, comp):
        '''
        @brief Search for a given component in the stored elements, return a list of matching indices
        @param comp A component to search for
        @return a list of indices of matching components
        '''
        return [i for i, component in enumerate(self.elements) if component == comp]
        
    def findAndPop(self, attribute, value):
        '''
        @brief Similar to find() but removes the matching entries from the list
        @param attribute The attribute to find
        @param value The value of the attribute to find
        @return a list of indices that were found and removed
        '''
        matches = self.find(attribute, value)
        indices = []
        for match in matches:
            indices.append(self.elements.pop())
            
        return indices  
     
    def sort(self, attribute=None):
        '''
        @brief Sort the list alphanumerically by a given attribute.  
        @param attribute (Opt) An attribute to sort the list by
        
        All children must override this with the attribute keyword set
        '''
        def chunkify(s):
            '''@brief return a list of numbers and non-numeric substrings of str
        
            the numeric substrings are converted to integer, non-numeric are left as is
            '''
            chunks = re.findall("(\d+|\D+)",s)
            chunks = [re.match('\d',x) and int(x) or x for x in chunks] #convert numeric strings to numbers
            return chunks   
                 
        def sortAttr(a, b):
            '''
            @brief Compare elements by an attribute
            '''
            chunka = chunkify(a.getAttribute(attribute))
            chunkb = chunkify(b.getAttribute(attribute))
            
            return cmp(chunka, chunkb)
        
        
        return self.elements.sort(sortAttr)    
    
     
if __name__ == "__main__":
    pass
    