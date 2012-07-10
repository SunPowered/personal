'''
Created on 2012-07-08

@author: timvb
'''
import os
import unittest
import re

from spice.netlist import SpiceNetlist, SpiceNetlistError
from schematic.netlist import NetlistError

class SpiceNetlistInitTest(unittest.TestCase):


    def setUp(self):
        self.file_name = 'schmitt.trigger.cir'
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.file_path = os.path.join(self.data_path, self.file_name)

    def tearDown(self):
        pass


    def testNoError(self):
        '''
        test no error on SpiceNetlistInit
        '''
        try:
            SpiceNetlist(self.file_path)
        except SpiceNetlistError, msg:
            self.fail("SpiceException returned with message: %s"%(msg))

    def testFileName(self):
        '''
        Test whether the file naming is working
        '''
        #Test that the testing file exists
        self.assertTrue(os.path.isfile(self.file_path), "Test file does not exist: %s"%(self.file_path))
        n = SpiceNetlist(self.file_path)
        #self.assertTrue(isinstance(n,netlist.Netlist), "Returned object not of type Netlist")
        
        bad_file_path = os.path.join(os.path.dirname(__file__), 'data', 'idontexist.cir')
        self.assertRaises(NetlistError, SpiceNetlist, bad_file_path)
        
        
        tmp_file_name = n.getTempFileName()
        try:
            name, ext = tmp_file_name.split('.tmp')
        except:
            self.fail("No .tmp in temp file name")
        working_file_path = os.path.dirname(self.file_path)
        
        #Check that the working directory of both original and temp files are equal
        self.assertEquals(working_file_path, os.path.dirname(n.getTempFilePath()), "Working file paths of temp and original netlist not equal. \n%s\n%s"%(working_file_path, os.path.dirname(n.getTempFilePath())))
        
        #self.assertEquals(n.getTempFilePath(), working_file_path, "Working file_path not working.  Expected %s, got %s"%(working_file_path, n.getTempFilePath()))

class SpiceNetlistTest(unittest.TestCase):


    def setUp(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'data', 'schmitt.trigger.cir') 
        self.netlist = SpiceNetlist(self.file_path)
        
        self.dummy_file_path = os.path.join(os.path.dirname(__file__), 'data', 'dummy.cir')
        self.dummy_netlist = SpiceNetlist(self.dummy_file_path)
        
    def testGetTemplate(self):
        import string
        template = self.netlist.getTemplate()
        self.assertTrue(isinstance(template, string.Template), "getTemplate not returning a string.Template object")
        
    def testParseVariables(self):
        expected_variables = ["var1", "var2"]
        r = self.dummy_netlist.parseVariables()
        self.assertIsNotNone(r, "Variables is None")
        self.assertEquals(r, expected_variables, "Not returning the correct number of variables from parse_variables. Expected %i, Got %i"%(len(expected_variables), len(r)))
        
        self.assertEqual(self.dummy_netlist.getVariables(), expected_variables, "Incorrect variables being parsed.  Expected %s, got %s"%(expected_variables, self.netlist.getVariables()))
        
    def testSubstituteVariables(self):
        variable_vector = {"var1":"1k", "var2":"10nF"}
        tmp_f = self.dummy_netlist.getTempFilePath()
        
        #Remove dummy file to ensure a new copy and insert vars
        try:
            os.remove(tmp_f)
        except:
            pass
        self.dummy_netlist.substituteVariables(variable_vector)  
        
        self.assertTrue(os.path.isfile(tmp_f), "Dummy netlist file was not written: %s"%(tmp_f))
        
        #Read back dummy file data
        file_data = open(tmp_f, 'r').read()
        matches = re.findall(r"^(\w+\s+){3}(\w+)$", file_data, re.MULTILINE)
        self.assertEquals(len(matches), len(variable_vector), "Improper match on variable insert") 

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()