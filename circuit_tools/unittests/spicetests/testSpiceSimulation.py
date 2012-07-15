'''
Created on 2012-07-06

@author: timvb

This test suite contains all the necessary testing procedures for the spice simulation object

A simulation should go as follows:

1.  A circuit is created in gschem, with or without variables.  And saved as mycircuit.sch
    1.1 There should be various subclasses of a Circuit object
        1.1.1 Spice Circuit
        1.1.2 Components Circuit
2.  The simulation variables are defined, if none, then a single pass should be performed
    2.1. Simulation Variable is a custom object, with default, bounds, and values attributes
    2.2 a getVariablesFromFile() method exists to parse from a config file (maybe YAML?)

in python
    >>>cir = circuit.Circuit('mycircuit.sch')
    >>>circuit_vars = cir.parseCircuitVariables()
    >>>sim = spice.simulation.Simulation(cir)

with sim. variables
    >>>sim_vars = spice.simulation.getVariablesFromFile(sim_definition_file)
    >>>sim.setVariables(sim_vars)
    
    >>>options={}
    >>>result = sim.run(**options) 
    
plot results
    >>>save_file = 'results.png'
    >>>print result.plotAll(save_file)
'''
import os

import unittest

import spice.simulation.simulation as simulation
import spice.circuit as cir


class TestSpiceSimulationInit(unittest.TestCase):


    def setUp(self):
        self.circuit_file_name = 'schmitt.trigger.sim.sch'
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.circuit_file_path = os.path.join(self.data_path, self.circuit_file_name)
        
        self.circuit = cir.SpiceCircuit(self.circuit_file_path)
        self.sim_vars = self.circuit.parseVariables()
        
        

    def testCircuitInputArg(self):
        '''
        test no error on init with circuit input arg
        '''
        try:
            simulation.SpiceSimulation(self.circuit)
        except Exception, msg:
            self.fail("Error raised with circuit object input arg: %s"%(msg))
            
    def testFileInputArg(self):
        '''
        test no error on init with a file as an input arg
        '''
        try:
            sim = simulation.SpiceSimulation(self.circuit_file_path)
        except Exception, msg:
            self.fail("Error raised with file path input arg: %s"%(msg))
    
    def testBadInputArgs(self):
        '''
        test bad inputs
        '''       
        cir = 'bad_file_name'
        self.assertRaises(simulation.SpiceSimulationError, simulation.SpiceSimulation, cir)



class SimulationInputVariableTest(unittest.TestCase):
    '''
    Tests the spice simulation input variable object
    '''       
    
    def setUp(self):
        self.name = 'test_variable'
        self.default = '1.5'
        self.bounds = [1e3, 5e3]
        self.num_values = 10
        
    def initTestVar(self):
        self.var = simulation.SimulationInputVariable(self.name, 
                                                 default=self.default, 
                                                 bounds=self.bounds)  
        
        self.assertIsNotNone(self.var, "None sim object returned")  
        self.assertIsNotNone(self.var.getBounds(), "Empty Bounds returned")
        self.assertIsNotNone(self.var.getDefault(), "Empty default returned")
        
    def testNoErrorOnInit(self):
        '''
        test no error on init
        '''
        try:
            self.initTestVar()
        
        except Exception, msg:
            self.fail("Error on simulation variable init: %s"%(msg))

    def testSetGetMethods(self):
        '''
        test set get methods
        '''
        self.initTestVar()
        
        
        #Bounds
        self.assertEquals(self.var.getBounds()[0],float(self.bounds[0]), "First Bounds element not equal")
        self.assertEquals(self.var.getBounds()[1],float(self.bounds[1]), "Second Bounds element not equal")
        
        #Name
        self.assertEquals(self.var.getName(), self.name, "Name attribute not correct")
        
        #Default
        #var_default = self.var.getDefault()
        #orig_default = self.default
        self.assertEquals(self.var.getDefault(), float(self.default), "Default not correct")
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()