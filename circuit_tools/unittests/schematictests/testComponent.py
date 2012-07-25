'''
Created on 2012-07-08

@author: timvb

'''
import unittest

from schematic.component import Component, ComponentList

class ComponentTest(unittest.TestCase):
    
    def setUp(self):

        self.attrs1 = {'device': 'RESISTOR',
                 'refdes': 'R1',
                 'value':'1k',
                 'manufacturer':'Panasonic',
                 'part_number':'ERJ-3GEYJ102V',
                 'footprint':'0603'}
        self.component1 = Component(**self.attrs1)
        
        self.attrs2 = self.attrs1
        self.component2 = Component(**self.attrs2)
        
        self.attrs3 = {'device': 'CONNECTOR',
                 'refdes': 'CONN1',
                 'manufacturer':'JST',
                 'part_number':'S2B-PH-SM4-TB',
                 'footprint':'JST_S2B-PH-SM4-TB'}       
        
        self.component3 = Component(**self.attrs3)
        
    def testEq(self):
        self.assertEqual(self.component1, self.component2, "__eq__ not correct")
        
        self.assertNotEqual(self.component1, self.component3, "Not equals not correct")
        
    def testAttributesAsDict(self):
        for i in range(1,4):
            a = getattr(self, 'attrs'+str(i))
            b = getattr(self, 'component'+str(i)).getAllAttributesAsDict()
            for attr in a.keys():
                if attr not in b.keys():
                    self.fail("Attribute %s never made it into Component%i"%(attr, i))
                
                self.assertEqual(a[attr], b[attr], "Attribute %s value not equal for Component%i"%(attr, i))
    
    def tearDown(self):
        pass

class ComponentListInitTest(unittest.TestCase):
    
    def testInit(self):
        try:
            cl = ComponentList()
        except Exception, msg:
            self.fail("Init broken: %s"%())
            
    def testInitWithIterable(self):
        iterable = [
                    Component(refdes='CONN1',
                              device='CONNECTOR',
                              manufacturer='JST',
                              part_number='S2B-PH-SM4-TB',
                              footprint='JST_S2B-PH-SM4-TB'),
                    Component(refdes='R1',
                              device='RESISTOR',
                              value='1k',
                              manufacturer='Panasonic',
                              part_number='ERJ-3GEYJ102V',
                              footprint='0603')
                    ]
        
        try:
            cl = ComponentList(iterable)
        except Exception, msg:
            self.fail("Failed with iterable argument.  Msg: %s"%(msg))
            
class ComponentListTest(unittest.TestCase):
    '''
    Features to test:
    
    Append, find, findIndex, findIndexByComponent, findAndPop
    '''
    def generateTestComponents(self):
        
        components = []
        
        def newComponent(**attributes):
            comp = Component(**attributes)
            components.append(comp)
        
        attrs = {'manufacturer':'JST',
                 'part_number':'S2B-PH-SM4-TB'}
        newComponent(**attrs)

        attrs = {'manufacturer':'Microchip',
                 'part_number':'MCP6002-I/SN'}
        newComponent(**attrs)
        
        attrs = {'manufacturer':'Vishay Siliconix',
                 'part_number':'SI2302ADS-T1-E3'}
        newComponent(**attrs)
        
        attrs = {'manufacturer':'Panasonic',
                 'part_number':'ERJ-3GEYJ102V'}
        newComponent(**attrs)
        
        attrs = {'manufacturer':'Stackpole Electronics',
                 'part_number':'RHC2512FT10R0'}
        newComponent(**attrs)
        
        return components        
        
        
    def setUp(self):
        self.cl = ComponentList(self.generateTestComponents())


    def tearDown(self):
        del self.cl


    def testSetup(self):
        self.assertEqual(len(self.cl), 5, "Setup not working")
        
    def testAppend(self):
        self.cl = ComponentList()
        components = self.generateTestComponents() 
        for item in components:
            self.cl.append(item)
            
        self.assertEqual(len(components), len(self.cl), "Append not correct")
        
        self.assertEqual(components[2], self.cl[2], 'Component 2 not equal')

    def testFind(self):
        jst_part = self.cl.find('manufacturer', 'JST')
        self.assertTrue(jst_part, "No JST part found: %s"%(str(jst_part)))
        
        ti_part = self.cl.find('manufacturer', 'TI')
        self.assertFalse(ti_part, "TI search returned not false: %s"%(str(ti_part)))
    
    def testFindIndexByComponent(self):
        
        for i in range(len(self.cl)):
            comp = self.cl[i]
            self.assertEqual(self.cl.findIndexByComponent(comp), [i], "findIndex not correct for component %s at index %i"%(comp, i))
    
    def testFindIndex(self):
        index = 2
        attribute = 'manufacturer'
        
        comp = self.cl[index]
        
        comp_index = self.cl.findIndex(attribute, comp.getAttribute(attribute))
        
        self.assertTrue(comp_index, "nothing returned for findIndex: %s"%(comp_index))
        self.assertEqual(comp_index[0], index, "Improper Index returned. Expected %i. Got %i"%(index, comp_index[0]))
        
    def testFindAndPop(self):
        original_length = len(self.cl)
        index = 2
        
        comp  = self.cl[index]
        comp_manufacturer = comp.getAttribute('manufacturer')
        self.assertTrue(self.cl.findIndexByComponent(comp), "Component %s for index %i not found"%(comp, index))
        
        comp2 = self.cl.findAndPop('manufacturer', comp_manufacturer)
        self.assertTrue(comp2, "Nothing returned from findAndPop")
        self.assertEqual(type(comp), type(comp2[0]), "Comp1 and 2 are not equal: %s \n %s"%(comp, comp2))
        self.assertEqual([comp], comp2, "Find and pop not popping the correct item")
        self.assertFalse(self.cl.findIndexByComponent(comp2[0]), "findAndPop not working")
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()