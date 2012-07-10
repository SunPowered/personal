'''
Created on 2012-07-06

@author: timvb
'''
import os
import numpy as np

import spice_read
from utils import log
import spice.circuit as cir

_default_array_length = 10

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
    
    @input:
        circuit - A Circuit object that is ready for simulation
        name (Optional) - The name of the simulation
        logger (Optional) - The logger instance to use 
        raw_file(Optional) - A custom name to assign to raw file output
        
    A simulation can be a one-time run or many, with the results being 
    '''

    _default_sim_name = "Spice Simulation"
    
    #_enums = {"Simulation Types":{"Single": 0, "Single Variable Sweep":1, "All Variable Sweep":2, "Optimize":3}}
    _default_raw_file = "results.raw"
    
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
            self.name = circuit.getName()
        else:
            self.name = name
        
        self.raw_file = raw_file
        
        #Circuit Variables 
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
        self.name = name
        
    def getName(self):
        return self.name
    
    def getSimVars(self):
        return self.sim_variables.keys()
    
    def getSimVarRange(self, var_name):
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
        
    def setSimVariableValuesFromBounds(self, var_name, n=_default_array_length, type_='lin'):
        '''
        creates an n length object of values, separated by the type.
        
        type: 
            lin - linearly spaced
            log - logarithmically spaced
        '''
        lower_bound, upper_bound = self.getSimVariableBounds(var_name)
        
        if type_ == "lin":
            
            self.sim_variables[var_name]["values"] = np.linspace(lower_bound, upper_bound, n)
            
        elif type_ == "log":
            
            self.sim_variables[var_name]["values"] = np.logspace(lower_bound, upper_bound, n)
            
    def setSimVariableBoundsFromValues(self, var_name):
        
        lower_bound = min(self.getSimVariableValues(var_name))
        upper_bound = max(self.getSimVariableValues(var_name))
        
        self.setSimVariableBounds(var_name, lower_bound, upper_bound)
        
    
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
        self.netlist = self.circuit.generateSpiceNetlist(logger=self.logger, **kwargs)
    
    def _runSpice(self, netlist):
        
        return os.system('ngspice -b -r %s %s'%(self.raw_file, netlist))
    
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

class SimulationResultError(Exception):
    pass
     
class SimulationResult(object):
    
    _default_dependent_output_variable='time'
    
    '''
    An object to store simulation results from many individual simulations.  
    
    It may need to be created and configured for each simulation run which is performed. 
    
    Should have the ability to read raw ngspice data and store relevant data persistently
    
    Also have the capability to plot?
    '''
    
    def __init__(self, sim_type=None, variables=None, save_vectors=None, raw_file=None):
        '''
        A Result file must be created before the simulation is run.  It is used by the simulator to track which data sets to track
        
        TOD: Define this in detail, it seems it will be important
        '''   
        
        #TODO: check sim_type is valid
        self.sim_type = sim_type
        
        self.variables = variables
        
        #Save_vectors list init
        if not save_vectors:
            self.save_vectors = []
        else:
            self.save_vectors = save_vectors
        
        #Init save vectors as attributes
        for vec in self.save_vectors:
            self.__setattr__(vec, np.array([]))
            
        #Init raw_file
        self.raw_file = raw_file
        
    def setSimType(self, sim_type):
        self.sim_type = sim_type    
    
    def getSimType(self):
        return self.sim_type
    
    def setRawFile(self, raw_file_path):
        if not os.path.isfile(raw_file_path):
            raise SimulationResultError("Raw File not found: %s"%(raw_file_path))
        self.raw_file = raw_file_path
        
    def getRawFile(self):
        return self.raw_file
    
    def readRawFile(self, raw_file_path=None):
        if not raw_file_path:
            raw_file_path = self.getRawFile()
            
        spice_data = spice_read.SpiceRead(raw_file_path).getPlots()
        
        #TODO: append spice data to save_vectors ...
        # Raw files should have single values plots in the first plot
        # time, frequency vectors in a plot should be understood

class SimulationVariableError(Exception):
    pass

class SimulationInputVariableError(SimulationVariableError):
    pass

class SimulationVariable(object):
    '''
    Base Class for Simulation Variables
    '''
    def __init__(self, name=None, units=None, logger=None):
        self.logger=logger
        self.name = name
        self.units = units
        
    def setUnits(self, units):
        self.units = units
    
    def getUnits(self):
        return self.units
    
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
    
    
class SimulationInputVariable(SimulationVariable):
    '''
    Custom object to hold a simulation input variable data
    '''
    
    def __init__(self, name=None, description=None, default=None,
                 bounds=None, values=None, units=None, logger=None):
        '''
        @input:
        (Optional)
            name            Printing name of the variable
            circuit_name    reference in circuit
            
        '''
        SimulationVariable.__init__(self, name=name, units=units, logger=None)
        
        self.description = description
        
        if not default:
            default = 0.0
        self.setDefault(default)
        
        if not bounds:
            bounds = []
        self.setBounds(bounds)
        
        self.setValues(values)
        
    def setDescription(self, description):
        '''
        '''
        self.description = description
        
    def getDescription(self):
        '''
        '''
        return self.description

    def setDefault(self, default):
        '''
        a float
        '''
        try:
            self.default = float(default)
        except:
            pass
    def getDefault(self):
        '''
        '''
        return self.default
    
    def setBounds(self, bounds, *arg):
        '''
        Bounds must be a 1x2 array [lower_bound, upper_bound]
        
        Can accept either a list(or numpy array) single input,
            or a lower_bound, upper_bound argument pair
        '''
        if len(arg) > 0:
            #lower_bound, upper_bound pair
            lower = float(bounds)
            upper = float(arg[0])
        else:
            try:
                lower = float(bounds[0])
                upper = float(bounds[1])
            except:
                lower = upper = 0.0
        
        try:
            self.bounds = np.array([lower, upper])
        except Exception, msg:
            raise SimulationInputVariableError("Error while setting the bounds. [Lower,Upper]: [%.2f,%.2f]\n%s"%(lower, upper, msg))
    
    def getBounds(self):
        '''
        '''
        return self.bounds
    
    def setValues(self, values):
        '''
        sets the variable values
        
        if input argument is a list, then a numpy array will be created in its place
        '''
        if isinstance(values, list):
            
            self.values = np.array(values)
            
        elif isinstance(values, np.ndarray):
            
            self.values = values
        
    def getValues(self):
        '''
        '''
        return self.values
    
    def setValuesFromBounds(self, length=None, spacing='lin'):
        '''
        sets the values of the variable from the saved bounds, the array length,
        and the spacing type (log or lin) to use.
        '''
        if not length:
            length = _default_array_length
        
        bounds = self.getBounds()
        if not bounds:
            raise SimulationInputVariableError("No bounds set")
        lower = bounds[0]
        upper = bounds[1]
        
        if spacing == 'lin':
            
            self.setValues(np.linspace(lower, upper, length))
            
        elif spacing == 'log':
            
            self.setValues(np.logspace(lower, upper, length))
        
        return self.getValues()
    
    def setBoundsFromValues(self):
        '''
        sets the bounds from a values array
        '''
        
        lower = min(self.getValues())
        upper = max(self.getValues())
        
        self.setBounds(lower, upper)
        
        return self.getBounds()