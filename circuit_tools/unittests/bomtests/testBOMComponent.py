'''
Created on 2012-07-08

@author: timvb
'''
import unittest

from bom.component import BOMComponent, BOMComponentList

class TestBomComponentList(unittest.TestCase):
    def generateTestComponents(self):
        
        components = []
        
        def newComponent(**attributes):
            comp = BOMComponent(**attributes)
            components.append(comp)
        
        attrs = {'refdes':'CONN1',
                 'device': 'CONNECTOR',
                 'manufacturer':'JST',
                 'part_number':'S2B-PH-SM4-TB'}
        newComponent(**attrs)

        attrs = {'refdes':'CONN2',
                 'device': 'CONNECTOR',
                 'manufacturer':'JST',
                 'part_number':'S2B-PH-SM4-TB'}
        newComponent(**attrs)
        
        attrs = {'refdes':'U1',
                 'device': 'OP AMP',
                 'manufacturer':'Microchip',
                 'part_number':'MCP6002-I/SN'}
        newComponent(**attrs)
        
        attrs = {'refdes':'Q1',
                 'device': 'NMOS',
                 'manufacturer':'Vishay Siliconix',
                 'part_number':'SI2302ADS-T1-E3'}
        newComponent(**attrs)
        
        attrs = {'refdes':'R1',
                 'device': 'RESISTOR',
                 'manufacturer':'Panasonic',
                 'part_number':'ERJ-3GEYJ102V'}
        newComponent(**attrs)

        attrs = {'refdes':'R3',
                 'device': 'RESISTOR',
                 'manufacturer':'Panasonic',
                 'part_number':'ERJ-3GEYJ102V'}
        newComponent(**attrs)
                
        attrs = {'refdes':'R2',
                 'device': 'RESISTOR',
                 'manufacturer':'Stackpole Electronics',
                 'part_number':'RHC2512FT10R0'}
        newComponent(**attrs)
        
        attrs = {'refdes':'R4',
                 'device': 'RESISTOR',
                 'manufacturer':'Stackpole Electronics',
                 'part_number':'RHC2512FT10R0'}
        newComponent(**attrs)
        
        return components

    def setUp(self):
        self.cl = BOMComponentList(self.generateTestComponents())

    def testSetup(self):
        comps = self.generateTestComponents()
        self.assertTrue(len(comps)>0, "Problem generating components\n%s"%(comps))
        
    def tearDown(self):
        del self.cl


    def testQuantities(self):
        jst_part = self.cl.find('manufacturer', 'JST')
        self.assertTrue(jst_part, "No JST part found")
        expected = 2
        jst_part = jst_part[0]
        self.assertEqual(jst_part.getQuantity(), expected, "Quantities not correct. Expected: %i. Got: %i"%(expected, jst_part.getQuantity()))

    def testTotalPartNumber(self):
        total_part_number = len(self.generateTestComponents())
        self.assertEqual(self.cl.total_number_parts, total_part_number, "Expected %i.  Got %i."%(total_part_number, self.cl.total_number_parts))
        
    def testTotalUniquePart(self):
        total_unique_parts = 5
        cl_total_unique_parts = self.cl.total_unique_parts
        
        self.assertEqual(total_unique_parts, cl_total_unique_parts, "Unique parts not equal.  Expected %i, Got %i"%(total_unique_parts, cl_total_unique_parts))
        
    def testRefdesTracking(self):
        manufacturer = "JST"
        occurances = 2
        indices = self.cl.findIndex('manufacturer', manufacturer)
        self.assertTrue(indices, "Nothing found for manufacturer %s"%(manufacturer))
        
        part = self.cl[indices[0]]
        refdes = part.getAttribute('refdes')
        
        self.assertTrue(isinstance(refdes, list), "Refdes is not a list. %s"%(refdes))
        self.assertEqual(len(refdes), occurances, "Incorrect occurances of refdes for manufacturer %s\nExpected %i Got %i"%(manufacturer, occurances, len(refdes)))
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()