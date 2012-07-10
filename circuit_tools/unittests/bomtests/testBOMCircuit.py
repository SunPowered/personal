'''
Created on 2012-07-08

@author: timvb
'''
import os
import unittest

from bom.circuit import BOMCircuit

class CircuitComponentTest(unittest.TestCase):
    '''
    Circuit Component Test Case
    
    Each circuit should be able to parse a schematic file
    
    Each circuit should store and maintain a components_list and unique_components_list
    
    No variables allowed when parsingComponents
    
    Each component must be checked against any required_attributes
    
    
    
    Tests all basic functionality of the Circuit class.
    
    The following tests must be passed:
        1. A parseVariables function to check whether any variables exist
        
        
    '''
    
    def setUp(self):
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        os.chdir(self.data_path)
        self.file_path = os.path.join(self.data_path, 'schmitt.trigger.sch') 
        self.cir = BOMCircuit(self.file_path)
        
        #self.dummy_file_path = os.path.join(os.path.dirname(__file__), 'data', 'dummy.cir')
        #self.dummy_c = Netlist(self.dummy_file_path)
        
    def testComponentParse(self):
        
        self.cir.parseComponents()
        self.assertTrue(len(self.cir.getComponentList()) > 0, "Empty component list")
        #self.assertTrue(len(self.cir.getUniqueComponents()) > 0, "Empty Unique Component List")
        
        
class CircuitComponentParseHierarchical(object):
    '''
    TODO:  Test hierarchical traversal
    '''
    pass
        
    """    
    def testParseVariables(self):
        expected_variables = ["var1", "var2"]
        r = self.dummy_c.parseVariables()
        self.assertIsNotNone(r, "Variables is None")
        self.assertEquals(r, expected_variables, "Not returning the correct number of variables from parse_variables. Expected %i, Got %i"%(len(expected_variables), len(r)))
        
        self.assertEqual(self.dummy_c.getVariables(), expected_variables, "Incorrect variables being parsed.  Expected %s, got %s"%(expected_variables, self.c.getVariables()))
        
    def testSetVariables(self):
        variable_vector = {"var1":"1k", "var2":"10nF"}
        tmp_f = self.dummy_c.getTempFilePath()
        
        #Remove dummy file to ensure a new copy and insert vars
        try:
            os.remove(tmp_f)
        except:
            pass
        self.dummy_c.setVariables(variable_vector)  
        
        self.assertTrue(os.path.isfile(tmp_f), "Dummy circuit file was not written: %s"%(tmp_f))
        
        #Read back dummy file data
        file_data = open(tmp_f, 'r').read()
        matches = re.findall(r"^(\w+\s+){3}(\w+)$", file_data, re.MULTILINE)
        self.assertEquals(len(matches), len(variable_vector), "Improper match on variable insert") 
    """




class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()