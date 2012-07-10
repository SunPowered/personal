'''
Created on 2012-06-27

@author: timvb

tests the circuit module for TvBSpice
'''
import unittest
from schematic.netlist import Netlist, NetlistError
import re
import os

import utils.log


class NetlistInitTest(unittest.TestCase):
    '''
    Test netlist initialization
    
    Netlist Init must pass the following tests:
    
        1. Assert that the file_path exists
        2. If the name keyword is not provided the file_path without extension should be used
            i.e. 'my_netlist.cir' gets a name of 'my_circuit'
        3. A working file name must also be created based off the file name input argument
    '''
    def setUp(self):
        self.file_name = 'schmitt.trigger.cir'
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.file_path = os.path.join(self.data_path, self.file_name)
        
    def testInit(self):
        '''
        Test general netlist init
        '''
        n = Netlist(self.file_path)
        self.assertTrue(isinstance(n, Netlist), "Returned object not of type Netlist")
        
            
    def testName(self):
        expected_name = 'schmitt.trigger'
        new_name = "a new name"
        c = Netlist(self.file_path)
        self.assertEquals(c.getName(), expected_name, "Auto-naming not correct.  Expected %s, got %s"%(expected_name, c.getName()))
        c.setName(new_name)
        self.assertEqual(c.getName(), new_name, "(set|get)_name not working")
        

class NetlistTest(unittest.TestCase):
    '''
    Main Circuit Test Case
    
    Tests all basic functionality of the Circuit class.
    
    The following tests must be passed:
        1. A getTemplate function must return a string.Template of the circuit file
        2. A parseVariables function
        3. A setVariables function should insert the values given into a template of the file and write it to the 
            temp_file_path
        
    '''
    def setUp(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'data', 'schmitt.trigger.cir') 
        self.netlist = Netlist(self.file_path)
        
        self.dummy_file_path = os.path.join(os.path.dirname(__file__), 'data', 'dummy.cir')
        self.dummy_netlist = Netlist(self.dummy_file_path)    
    
    def testRemoveNetlistFile(self):
        '''
        removes the netlist file stored in memory, useful for cleanup procedures
        '''  
        #create backup of dummy_file
        dummy_file_backup = self.dummy_file_path + '.backup'
        open(dummy_file_backup, 'w').write(open(self.dummy_file_path, 'r').read())
        
        self.assertTrue(os.path.isfile(dummy_file_backup), "dummy_file_backup not created")
        #remove the netlist file
        self.dummy_netlist.removeNetlistFile()
        
        #Check file no longer exists
        self.assertFalse(os.path.isfile(self.dummy_file_path), 'Removal of netlist file was not successful')
        
        #Rewrite from backup file
        open(self.dummy_file_path, 'w').write(open(dummy_file_backup, 'r').read())
        
        #Replace dummy_netlist
        self.dummy_netlist = Netlist(self.dummy_file_path)
        
        #Remove the backup file
        os.remove(dummy_file_backup)
        
    def testCreateNetlistFromCircuit(self):  
        
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()