'''
@file spice/simulation/simulation.py
@package: spice.simulation.simulation
@author: timvb
@brief: The simulation module holding the base SPICE simulaton obect.

@details A Simulation Object reads schematic circuit object, as well as a model input.

@par The SpiceSimulation Object can be subclassed to provide different simulation types:
    @li @b SingleSimulation   Performs a single simulation pass
    @li @b ParameterSweepSimulation Sweeps through variables in the model input, storing single pass values
    @li @b OptimizationSimulation   Performs a differential optimization routine to find optimal values for a circuit 
'''

import os

import numpy as np

from utils import log, config, fs
import utils.config.spice_config as spice_config

from spice.netlist import SpiceNetlist
import spice.circuit as cir
from spice.simulation.variable import SimulationInputVariable
from spice.simulation.result import SimulationResult

#TODO: Eliminate these with subclasses
class SimulationTypesEnums(object):
    SINGLE = 0
    SINGLE_VARIABLE_SWEEP = 1
    ALL_VARIABLE_SWEEP = 2
    OPTIMIZE = 3
    
class SpiceSimulationEnums(object):
    SIM_ENUMS = SimulationTypesEnums
    


class SpiceSimulationError(Exception):
    pass

class SpiceSimulation(object):
    '''
    An object to run spice simulations using ngspice
    
    @todo: Prepare for breakup to subclasses
    
    @param circuit (Optional) A SpiceCircuit object that is ready for simulation
    @param netlist (Optional) A SpiceNetlist to run.  Must be present if no circuit argument provided.
    @param name   (Optional) - The name of the simulation
    @param raw_file  (Optional) - A custom name to assign to raw file output
    @param logger (Optional) - The logger instance to use 
        
    Simulations are composed of the following objects.
    
    Simulation Netlist
    Simulation Variables
    Simulation Result
    
    A single run of a circuit takes one set of variables, inserts them into a netlist, 
    runs the simulation, and returns a simulation result
        
    A simulation can be a one-time run or many, with the results being ...
    
    Usage:
    @code
    import spice.circuit.SpiceCircuit
    cir = SpiceCircuit('/location/to/circuit/file.sch')
    print cir 
    @endcode
    '''

    
    #_enums = {"Simulation Types":{"Single": 0, "Single Variable Sweep":1, "All Variable Sweep":2, "Optimize":3}}
    _default_raw_file_ext = spice_config.DEFAULT_SPICE_RESULTS_FILE_EXT
    
    def __init__(self, circuit=None, netlist=None, name=None, logger=None, raw_file=None, output_variables=None):
        '''
        Simulation constructor
        '''
        self.logger = logger or log.getDefaultLogger('spice.simulation.simulation.SpiceSimulation')
        #Assert circuit and netlist are not both defined simultaneously
        if circuit and netlist:
            raise SpiceSimulationError("Cannot give both circuit and netlist as input arguments")
        
        #Circuit Variables 
        self.output_variables = output_variables or []
        self.sim_variables = [] 
        
        #Results
        self.results = SimulationResult()
        
        #Add circuit
        self.setCircuit(circuit)
        
        #Add netlist
        if netlist:
            self.setNetlist(netlist)
        
        #Add name
        if not name:
            circuit_name = self.netlist.getName()
            if not circuit_name:
                name = config.DEFAULT_SPICE_SIMULATION_NAME
        else:
            self.name = name
        
        #Raw file
        self.raw_file_path = ''
        self.raw_file_name = ''
        self.setRawFile(file_name=raw_file)
        
        #Working directories
        self.original_working_directory = self.working_directory = os.getcwd()


    def setRawFile(self, file_name=None):
        '''
        Auto-generate a raw file name from the netlist
        '''
        netlist = self.getNetlist()
        if netlist:
            netlist_file_name = netlist.getFileName()
            raw_file_name = file_name or os.path.splitext(netlist_file_name)[0] + self._default_raw_file_ext
        
            self.raw_file_name = raw_file_name
            self.raw_file_path = os.path.join(os.path.dirname(netlist.getFilePath()), self.raw_file_name)
    
    def getRawFileName(self):
        return self.raw_file_name
    
    def getRawFilePath(self):
        return self.raw_file_path
    
        
    def setName(self, name):
        '''
        sets the simulation name
        '''
        self.name = name
        
        
    def getName(self):
        '''
        return the simulation name
        '''
        return self.name
    
    
    def getSimVariables(self):
        '''
        return all of the simulation variables
        '''
        return self.sim_variables
    
    
    def setCircuit(self, circuit):
        '''
        @brief Sets a new circuit file to use for simulation
        @throws spice.simulation.simulation.SpiceSimulationError If there is a problem with the crcuit given
        @param circuit Can be a str path to a schematic file or a spice.circuit.SpiceCircuit object
        
        '''
        if not circuit:
            self.circuit = None
            return
        
        if not isinstance(circuit, cir.SpiceCircuit):
            if isinstance(circuit, (str, unicode)):
                try:
                    circuit = cir.SpiceCircuit(circuit)
                except:
                    raise SpiceSimulationError("No schematic circuit file path given in arguments") 
            else:
                raise SpiceSimulationError("No schematic circuit given in arguments")
            
        self.circuit = circuit
        try:
            self.setNetlist(self.circuit.generateSpiceNetlist())
        except Exception, msg:
            self.logger.error("Error creating netlist: %s"%(msg))
        
            
    def setNetlist(self, netlist):
        '''
        @brief sets the current simulation netlist
        @param netlist a SpiceNetlist object
        @throws SpiceSimulationError if the object is not a SpiceNetlist object
        '''
        if not netlist:
            self.netlist = netlist
            return 
        elif not isinstance(netlist, SpiceNetlist ):
            raise SpiceSimulationError("netlist argument is not a SpiceNetlist object: %s"%(netlist))
        
        self.netlist = netlist
        self.parseVariables()
       
        
    def getNetlist(self):
        return self.netlist
    
    
    def setOutputVariables(self, variable_names):
        '''
        @brief Sets the Simulation Output variables
        '''
        for vector in variable_names:
            self.results.addOutputVector(vector)
       
        
    def parseVariables(self):
        '''
        checks the current netlist for variables and creates a new SpiceSimulationInput variable
        '''
        netlist = self.getNetlist()
        if netlist:
            self.netlist_vars = netlist.parseVariables()
            for var in self.netlist_vars:
                self.sim_variables.append(SimulationInputVariable(name=var))
                self.results.addOutputVector(var)
            self.logger.debug("Parsed the following variables from netlist file: %s "%(str(self.netlist_vars)))

     
    def _checkSimulation(self):    
        '''
        Need to check the following things
        '''
        if not self._checkSimVariablesValues():
            raise SpiceSimulationError("Not all simulation variable values are complete")
        
        
        
    
    def _checkSimVariablesValues(self):
        '''
        checks the simulation variable values if they exist.  None can be empty
        '''
        
        result = True
        for var in self.getSimVars():
            result = result and (len(self.getSimVarRange(var))>0)
            if not result:
                self.logger.error("Sim Variable %s has empty values"%(var))
                return False
        return result 
    
        
    def _runSpice(self, netlist=None):
        '''
        Run a NGSPICE simulation in batch mode on the current netlist
        '''
        netlist = netlist or self.getNetlist()
        if not netlist:
            return None
        
        cmd = 'ngspice -b -a %s -r %s'%( netlist.getTempFilePath(), self.getRawFileName())
        if not config.DEBUG:
            result = os.system(cmd + ' 2>&1')
        else:
            result = os.system(cmd)
            
        if result != 0:
            self.logger.error("Ngspice run returned a fail result.  check the netlist: %s"%(netlist.getTempFilePath()))
        else:
            #If no error, check the raw file exists and read its results into
            #the results object
            
            fs.waitForFile(self.getRawFilePath())
        
            self.results.readRawFile(self.getRawFilePath())

    def _runSingle(self, input_variables=None):
        '''
        @brief run a single simulation
        @param input_variables a dict mapping of variable names and values to run.  If
        nothing is given, then the defaults will be used
        '''
        netlist = self.getNetlist()
        if netlist:
            #Sim Input Variables
            sim_vars = self.getSimVariables()
            
            variable_mapping = input_variables or {}
            
            if not variable_mapping:
                #If no variables provided, take the defaults
                for variable in sim_vars:
                    variable_mapping[variable.getName(), variable.getDefault()]
            netlist.substituteVariables(variable_mapping)
                
            self._runSpice()   
            
            
    def run(self):
        '''
        @todo: maybe make a quasi intelligent simulation runner based on variable states
        '''
        try:
            self._checkSimulation()
        except SpiceSimulationError, msg:
            raise SpiceSimulationError("Failed Simulation Check: %s"%(msg))
        self.logger.debug("Variables have been checked and are complete")
        
        
        sim_type = self.getSimType()
        result = None
        if sim_type == SimulationTypesEnums.SINGLE:
            result = self._runSingle()
            
        return result

    def runSetup(self):
        '''
        @brief Perform these actions at the start of each simulation
        '''
        #switch the working directory
        netlist = self.getNetlist()
        
        if not netlist:
            raise SpiceSimulationError("No netlist defined for simulation.  Aborting run")
        
        #Switch the working directory to that of the netlist's temp file
        self.working_directory = fs.switchWDFromFilePath(netlist.getTempFileName())
        
    def runTearDown(self):
        #Return the working directory
        os.chdir(self.original_working_directory)
        self.working_directory = self.original_working_directory
        
        
class SingleSimulationError(SpiceSimulationError):
    pass

class SingleSimulation(SpiceSimulation):
    '''
    @brief Class to perform a single simulation
    @details
    Running a single simulation looks a little something like this:
    The simulation conditions need to be checked first: 
    This includes: 
    @li check there is a valid netlist object stored
    @li Check whether there are any variables to substitute
    @li If yes, then take the default values for each variable, or take an input argument with the run method, with 
    {'var_name':value} pairs
    @li if no variables in netlist, then copy to the temp file
    @li single sim is run, results are saved in the local results attribute
    
    '''
    
    def __init__(self, **kwargs):
        SpiceSimulation.__init__(self, **kwargs)
        
    def run(self, input_variables=None):
        
        self.runSetup()
        self._runSingle(input_variables=input_variables)
        self.runTearDown()
        return self.results
    
 
        
        
    