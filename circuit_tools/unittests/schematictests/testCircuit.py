'''
Created on 2012-06-27

@author: timvb

tests the circuit module for TvB circuit tools
'''
import os

import unittest

from schematic.circuit import Circuit, CircuitError, CircuitFileError

class CircuitInitTest(unittest.TestCase):
    '''
    Test Circuit Init to ensure sanity 
    '''
    def setUp(self):
        self.file_name = 'schmitt.trigger.sch'
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.file_path = os.path.join(self.data_path, self.file_name)
        
    def testInit(self):
        '''
        Test general circuit init
        '''
        n = Circuit(self.file_path)
        self.assertTrue(isinstance(n,Circuit), "Returned object not of type Circuit")
        
        for file_name in ['idontexist.sch', 'dummy.cir']:
            bad_file_path = os.path.join(self.data_path, file_name)
            self.assertRaises(CircuitFileError, Circuit, bad_file_path)
        

        
    def testFileName(self):
        '''
        Test whether the file naming is working
        '''
        #Test that the testing file exists
        self.assertTrue(os.path.isfile(self.file_path), "Test file does not exist: %s"%(self.file_path))
        cir = Circuit(self.file_path)
        #self.assertTrue(isinstance(n,Netlist), "Returned object not of type Netlist")
        #Name should be auto generated from file path, check against self.file_name
        f_name = cir.getName()
        
        #self.assertEquals(f_name, os.path.splitext(self.file_name)[0], "Error in auto generated file names. %s : %s"%(f_name, self.file_name))
        
        
    def testName(self):
        '''
        Test set/get Name and name auto generation
        '''
        expected_name = os.path.splitext(self.file_name)[0]
        new_name = "a new name"
        c = Circuit(self.file_path)
        self.assertEquals(c.getName(), expected_name, "Auto-naming not correct.  Expected %s, got %s"%(expected_name, c.getName()))
        c.setName(new_name)
        self.assertEqual(c.getName(), new_name, "(set|get)_name not working")
        



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CircuitInitTest, 'test'))
    
    return suite

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()