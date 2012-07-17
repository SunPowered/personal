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

import numpy as np
from matplotlib import pyplot as plt

import spice.simulation.simulation as simulation
import spice.circuit as cir
from spice.netlist import SpiceNetlist

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

class TestSpiceSimulationInit(unittest.TestCase):
    '''
    @brief Test the SpiceSimulation Init procedure
    @todo add netlist arguments upon instantiation
    '''
    

    def setUp(self):
        self.circuit_file_name = 'schmitt.trigger.sim.sch'
        self.data_path = DATA_PATH
        self.circuit_file_path = os.path.join(self.data_path, self.circuit_file_name)
        
        self.circuit = cir.SpiceCircuit(self.circuit_file_path)
        self.sim_vars = self.circuit.parseVariables()
        
        

    def testCircuitInputArg(self):
        '''
        test no error on init with circuit input arg
        '''
        try:
            simulation.SpiceSimulation(circuit=self.circuit)
        except Exception, msg:
            self.fail("Error raised with circuit object input arg: %s"%(msg))
            
    def testFileInputArg(self):
        '''
        test no error on init with a file as an input arg
        '''
        try:
            sim = simulation.SpiceSimulation(circuit=self.circuit_file_path)
        except Exception, msg:
            self.fail("Error raised with file path input arg: %s"%(msg))
    
    def testBadInputArgs(self):
        '''
        test bad inputs
        '''       
        cir = 'bad_file_name'
        self.assertRaises(simulation.SpiceSimulationError, simulation.SpiceSimulation, {'circuit':cir})



class SimulationInputVariableTest(unittest.TestCase):
    '''
    Tests the spice simulation input variable object
    '''       
    
    def setUp(self):
        self.name = 'test_variable'
        self.default = '1.5'
        self.bounds = [1e3, 5e3]
        self.num_values = 10
        
    def initVariables(self):
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
            self.initVariables()
        
        except Exception, msg:
            self.fail("Error on simulation variable init: %s"%(msg))

    def testSetGetMethods(self):
        '''
        test set get methods
        '''
        self.initVariables()
        
        
        #Bounds
        self.assertEquals(self.var.getBounds()[0],float(self.bounds[0]), "First Bounds element not equal")
        self.assertEquals(self.var.getBounds()[1],float(self.bounds[1]), "Second Bounds element not equal")
        
        #Name
        self.assertEquals(self.var.getName(), self.name, "Name attribute not correct")
        #Default
        self.assertEquals(self.var.getDefault(), float(self.default), "Default not correct")
        
class TestSpiceSimulationSingleRun(unittest.TestCase):
    '''
    Test a single simulation pass.  RC Circuit from a netlist
    '''
    
    def setUp(self):
        self.file_path = os.path.join(DATA_PATH, 'rc_circuit.net')
        self.raw_file_name = 'single_rc.raw'
        self.raw_file_path = os.path.join(DATA_PATH, self.raw_file_name)
        file_str = '''*Spice netlist RC circuit
V1 in 0 dc 0 ac SIN(0 0 1kHz)
R1 in out 1k
C1 out 0 1uF
.ac dec 10 0.1 1MegHz
.save %s frequency v(out) 
.end
'''%(self.raw_file_path)
        open(self.file_path, 'w').write(file_str)
        self.netlist = SpiceNetlist(self.file_path)
        
    def testSim(self):
        output_vars = ["frequency", "v(out)"]
        sim = simulation.SingleSimulation(netlist=self.netlist, raw_file=self.raw_file_name)
        sim.setOutputVariables(output_vars)
        result = sim.run()
        plotVectors(result.frequency, np.abs(result.v_out), scale='log')
        plt.title('RC AC Analysis')
        plt.xlabel("Frequency")
        plt.ylabel("Abs(v_out)")
        plt.show()

class SimulationWithVariablesSingleTest(unittest.TestCase):
    '''
    @todo Run a single test on a circuit with variables
    '''
    def setUp(self):    
        pass    
def plotVectors(x, y, scale='linear'):
    plt.plot(x, y, 'k-')
    plt.xscale(scale)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()