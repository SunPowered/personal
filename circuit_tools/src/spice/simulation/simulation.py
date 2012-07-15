'''
@package: spice.simulation.simulation
@author: timvb
@brief: The simulation module holding the base SPICE simulaton obect.

A Simulation Object reads schematic circuit object, as well as a model input.

The SpiceSimulation Object can be subclassed to provide different simulation types:
    -- SingleSimulation    -    Performs a single simulation pass
    - ParameterSweepSimulation    -    Sweeps through variables in the model input, storing single pass values
    - OptimizationSimulation    -    Performs a differential optimization routine to find optimal values for a circuit 
'''

import os

import numpy as np

from utils import log, config
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
    
    @param circuit A Circuit object that is ready for simulation
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
    _default_raw_file = "spice_results.raw"
    
    def __init__(self, circuit, name=None, logger=None, raw_file=_default_raw_file):
        '''
        Simulation constructor
        '''
        if not logger:
            self.logger = log.getDefaultLogger('spice.simulation.SpiceSimulation')
        else:
            self.logger = logger
            
        if not isinstance(circuit, cir.SpiceCircuit):
            if isinstance(circuit, (str, unicode)):
                try:
                    circuit = cir.SpiceCircuit(circuit)
                except:
                    raise SpiceSimulationError("No schematic circuit file path given in arguments") 
            else:
                raise SpiceSimulationError("No schematic circuit given in arguments")
        
        self.circuit = circuit
        
        if not name:
            circuit_name = circuit.getName()
            if not circuit_name:
                name = config.DEFAULT_SPICE_SIMULATION_NAME
        else:
            self.name = name
        
        self.raw_file = raw_file
        
        #Circuit Variables 
        #TODO: Now use the custom container, variable.SimulationVariable
        '''
        The Variables dict has an internal structure of
        {"VariableName": {"default": default_value,
                         "bounds": numpy.ndarray([lower_bounds, upper_bounds])
                         "values": numpy.ndarray([value1, value2, ...])
                         },
        "VariableName2:{...},
        ...
        }
        '''
        self.sim_variables = []  
        ''' 
        var_template = {"default": None,
                        "values": np.array([]),
                        "bounds": np.array([0, 0])}
        '''
        for var in circuit.parseVariables():
            self.sim_variables.append(SimulationInputVariable(name=var))
        #self.sim_var_ranges = {}
        #[self.sim_var_ranges.__setitem__(key, np.array()) for key in self.sim_vars]
        #self.default_values = {}
        #[self.default_values.__setitem__(key, None) for key in self.sim_vars]
        
        
        self.netlist = self.circuit.generateSpiceNetlist()
        
        self.simulation_type = None
    
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
    
    def getSimVars(self):
        '''
        return all of the simulation variables
        '''
        return self.sim_variables.keys()
    
    #TODO: Delete due to existance in Variable object
    """
    def getSimVarRange(self, var_name):
        '''
        
        '''
        return self.sim_var_ranges[var_name]
    
    def getSimVariableBounds(self, var_name):
        return self.sim_variables[var_name]["bounds"]
    
    def getSimVariableDefault(self, var_name):
        return self.sim_variables[var_name]["default"]
    
    def getSimVariableValues(self, var_name):
        return self.sim_variables[var_name]["values"]
    
    def setSimVariableBounds(self, var_name, lower_bound, upper_bound):
        '''
        '''
        self.sim_variables[var_name]["bounds"][0] = lower_bound
        self.sim_variables[var_name]["bounds"][1] = upper_bound
        
    def setSimVariableDefault(self, var_name, value):
        '''
        '''
        self.sim_variables[var_name]["default"] = value
        
    def setSimVariableValues(self, var_name, values):
        '''
        '''
        self.sim_variables[var_name]["values"] = values
        
    def setSimVariableValuesFromBounds(self, var_name, n=None, type_='lin'):
        '''
        creates an n length object of values, separated by the type.
        
        type: 
            lin - linearly spaced
            log - logarithmically spaced
        '''
        if not n:
            n = config
        lower_bound, upper_bound = self.getSimVariableBounds(var_name)
        
        if type_ == "lin":
            
            self.sim_variables[var_name]["values"] = np.linspace(lower_bound, upper_bound, n)
            
        elif type_ == "log":
            
            self.sim_variables[var_name]["values"] = np.logspace(lower_bound, upper_bound, n)
            
    def setSimVariableBoundsFromValues(self, var_name):
        
        lower_bound = min(self.getSimVariableValues(var_name))
        upper_bound = max(self.getSimVariableValues(var_name))
        
        self.setSimVariableBounds(var_name, lower_bound, upper_bound)
    #TODO: Variable methods end here    
    """
    def getSimType(self):
        return self.simulation_type
    
    def setSimType(self, type_):
        self.simulation_type = type_
            
    """    
    def setSimulationVariableByBounds(self, var_name, values):
        '''
        Sets a single simulation variable, var_name to the values
        given in values
        
        Values can be any array of length 2, [lower_bounds, upper_bounds] entry, and a
        values array will be generated
        '''    
        
        if not isinstance(values, list):
            raise SpiceSimulationError("values must be given as a list")
        if len(values) == 1:
            values = [0, values[0]]
        if not len(values) == 2:
            raise SpiceSimulationError("values requires a [lower_bound, upper_bound] format")
        
        
        
        self.setSimulationVariable(var_name, np.arange(values[0], values[1], (values[1] - values[0]) *1.0 / self._default_array_length))
    
    def setSimulationVariable(self, type_, var_name, values):
        '''
        Sets a variable to a value.
        
        The value must be a list or numpy array
        '''
        if not isinstance(values, (list, np.ndarray)):
            raise SpiceSimulationError("values must be given as a list or numpy array")
        
        if not var_name in self.getSimVars():
            raise SpiceSimulationError("Variable %s does not exist in circuit: %s"%(var_name, self.circuit.getName()))
        
        self.sim_var_ranges[var_name] = np.array(values)
        
    def setSimulationVariableValuesByDict(self, values_dict):
        '''
        allows programatically setting all variable values with a dict
        
        values_dict = {var_name1: list1, var_name2:}
        '''
        if not isinstance(values_dict, dict):
            raise SpiceSimulationError("values_Dict must be a dict object")
 
        for var_name in values_dict.get_keys():
            if not var_name in self.getSimVars():
                raise SpiceSimulationError("Error with values_dict.  Var Name %s non existent in circuit")
            
            values = values_dict[var_name]
            if not isinstance(values, (list, np.ndarray)):
                raise SpiceSimulationError("Value of variable %s must be a list object"%(var_name))
            
            self.setSimulationVariable(var_name, values)   
    """         
    def _checkSimulation(self):    
        '''
        Need to check the following things
        '''
        if not self._checkSimVariablesValues():
            raise SpiceSimulationError("Not all simulation variable values are complete")
        
    def _checkRunType(self):
        '''
        Checks what sort of simulation can be run with the present simulator variables
        
        '''    
        
    
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
    

    def generateNetlist(self, **kwargs):
        '''
        generates a netlist from the current circuit
        '''
        self.netlist = self.circuit.generateSpiceNetlist(logger=self.logger, **kwargs)
    
    def _runSpice(self, netlist):
        '''
        Run a NGSPICE simulation in batch mode on the current netlist
        '''
        return os.system('ngspice -b -r %s %s'%(self.raw_file, netlist))
    
    #TODO: Fit all this under a subclass
    def _runSingle(self):
        '''
        Runs the variables with their default configuration, returns a simulation result object
        '''
        variables = {}
        result = SimulationResult(type_=SimulationTypesEnums.SINGLE, variables=self.getSimVars())
        
        for var_name in self.getSimVars():
            variables[var_name] = self.getSimVariableDefault(var_name)
            
        tmp_netlist = self.netlist.setVariables(variables) 
        self._runSpice(tmp_netlist)   
    
    def run(self):
        '''
        Runs the ngspice simulation
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


class SingleSimulation(SpiceSimulation):
    '''
    
    '''
