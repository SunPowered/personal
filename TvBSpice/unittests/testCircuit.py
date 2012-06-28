'''
Created on 2012-06-27

@author: timvb

tests the circuit module for TvBSpice
'''
import unittest
import circuit
import re
import os

class CircuitInitTest(unittest.TestCase):
    '''
    Test circuit initialization
    
    c = Circuit('my_circuit.cir')
    c = Circuit('my_circuit.cir', name='Excellent Electronics')
    
    Circuit Init must pass the following tests:
    
        1. Assert that the filename exists
        2. If the name keyword is not provided the filename without extension should be used
            i.e. 'my_circuit.cir' gets a name of 'my_circuit'
        3. A working file name must also be created based off the file name input argument
    '''
    def setUp(self):
        self.filename = self.filename = os.path.join(os.path.dirname(__file__), 'data', 'schmitt.trigger.cir')
        
    def testFileName(self):
       
        self.assertTrue(os.path.isfile(self.filename), "Test file does not exist: %s"%(self.filename))
        c = circuit.Circuit(self.filename)
        self.assertTrue(isinstance(c,circuit.Circuit), "Returned object not of type Circuit")
        
        bad_filename = self.filename = os.path.join(os.path.dirname(__file__), 'data', 'idontexist.cir')
        self.assertRaises(AssertionError, circuit.Circuit, bad_filename)
        
        working_filename = self.filename = os.path.join(os.path.dirname(__file__), 'data', 'schmitt.trigger.tmp.cir')
        self.assertEquals(c.get_temp_filename(), working_filename, "Working filename not working.  Expected %s, got %s"%(working_filename, c.get_temp_filename()))
        
    def testName(self):
        expected_name = 'schmitt.trigger'
        new_name = "a new name"
        c = circuit.Circuit(self.filename)
        self.assertEquals(c.get_name(), expected_name, "Auto-naming not correct.  Expected %s, got %s"%(expected_name, c.get_name()))
        c.set_name(new_name)
        self.assertEqual(c.get_name(), new_name, "(set|get)_name not working")

class CircuitTest(unittest.TestCase):
    '''
    Main Circuit Test Case
    
    Tests all basic functionality of the Circuit class.
    
    The following tests must be passed:
        1. A get_template function must return a string.Template of the circuit file
        2. A parse_variables function
        3. A insert_variables function should insert the values given into a template of the file and write it to the 
            temp_filename
        
    '''
    
    def setUp(self):
        self.filename = os.path.join(os.path.dirname(__file__), 'data', 'schmitt.trigger.cir') 
        self.c = circuit.Circuit(self.filename)
        
        self.dummy_filename = os.path.join(os.path.dirname(__file__), 'data', 'dummy.cir')
        self.dummy_c = circuit.Circuit(self.dummy_filename)
        
    def testGetTemplate(self):
        import string
        template = self.c.get_template()
        self.assertTrue(isinstance(template, string.Template), "get_template not returning a string.Template object")
        
    def testParseVariables(self):
        expected_variables = ["var1", "var2"]
        r = self.dummy_c.parse_variables()
        self.assertEquals(r, len(expected_variables), "Not returning the correct number of variables from parse_variables. Expected %i, Got %i"%(len(expected_variables), r))
        self.assertEqual(self.dummy_c.get_variables(), expected_variables, "Incorrect variables being parsed.  Expected %s, got %s"%(expected_variables, self.c.get_variables()))
        
    def testInsertVariables(self):
        variable_vector = {"var1":"1k", "var2":"10nF"}
        tmp_f = self.dummy_c.get_temp_filename()
        
        #Remove dummy file to ensure a new copy and insert vars
        try:
            os.remove(tmp_f)
        except:
            pass
        self.dummy_c.insert_variables(variable_vector)  
        
        self.assertTrue(os.path.isfile(tmp_f), "Dummy circuit file was not written: %s"%(tmp_f))
        
        #Read back dummy file data
        file_data = open(tmp_f, 'r').read()
        matches = re.findall(r"^(\w+\s+){3}(\w+)$", file_data, re.MULTILINE)
        self.assertEquals(len(matches), len(variable_vector), "Improper match on variable insert") 
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()