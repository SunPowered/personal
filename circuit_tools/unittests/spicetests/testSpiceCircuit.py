'''
Created on 2012-07-08

@author: timvb
'''
import os
import time
import unittest

from spice.netlist import SpiceNetlist
from spice.circuit import SpiceCircuit

def print_timing(func):
    def wrapper(*arg, **kwarg):
        t1 = time.clock()
        res = func(*arg, **kwarg)
        t2 = time.clock()
        print '%s took %i counts and took %0.3fms' % (func.func_name, res, (t2-t1)*1000.0)
        return res
    return wrapper

class CircuitGenerateSpiceNetlistTest(unittest.TestCase):
    '''
    Test spice netlist generation from a schematic circuit
    '''       
    @print_timing
    def waitForFileToExist(self, file_path, count=10, timeo=1):
        if (count == 0) or (os.path.isfile(file_path)):
            return count
        
        time.sleep(timeo)
        self.waitForFileToExist(count-1, timeo)
        
    def setUp(self):
        
        self.file_name = 'schmitt.trigger.sim.sch'
        self.netlist_file_name = 'schmitt.trigger.sim.cir'
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.file_path = os.path.join(self.data_path, self.file_name)
        self.cir = SpiceCircuit(self.file_path)
        try:
            os.remove(os.path.join(self.data_path, self.netlist_file_name))
        except OSError:
            pass
        self.netlist = self.cir.generateSpiceNetlist()
        self.waitForFileToExist(self.netlist.getFilePath())
    def testNoErrorAndType(self):
        '''
        test for no error on netlist generation and type return
        '''    
       
        self.assertTrue(isinstance(self.netlist, SpiceNetlist), "circuit spice netlist generator not returning a netlist object")
        
    def testVariablesAreParsable(self):
        '''
        test whether variables in both circuit and netlist are parsable
        '''

        circuit_variables = self.cir.parseVariables()
        netlist_variables = self.netlist.parseVariables()
        self.assertEqual(circuit_variables, netlist_variables , "Variables from schematic and netlist are not equal")
        
    def tearDown(self):
        self.netlist.removeNetlistFile()



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()