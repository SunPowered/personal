'''
@package spice.simulation.variable
@file spice/simulation/variable.py
@author: timvb
@brief Simulation Variables

'''

import numpy as np

from utils import config, log


class SimulationVariableError(Exception):
    pass

class SimulationInputVariableError(SimulationVariableError):
    pass

class SimulationVariable(object):
    '''
    @brief Base Class for Simulation Variables
    @todo Explain further.  What can a variable do?  What is it used for?
    '''
    def __init__(self, name=None, units=None, logger=None):
        '''
        @brief Constructor method
        @param name (Opt.) Variable name
        @param units (Opt.) The variable units
        @param logger (Opt.) A custom logger object to use 
        '''        
        self.logger = logger or log.getDefaultLogger('Simulation Variable')
        
        self.name = name
        self.units = units
        
    def setUnits(self, units):
        '''
        @brief Set units for a variable
        @param units The units to print back
        '''
        self.units = units
    
    def getUnits(self):
        '''
        @brief returns the units
        @return str Current units
        '''
        return self.units
    
    def setName(self, name):
        '''
        @brief sets the name to the variable
        @param name the name to assign
        '''
        self.name = name
        
    def getName(self):
        '''
        @brief returns the name
        @return str Current name
        '''
        return self.name
    
    
class SimulationInputVariable(SimulationVariable):
    '''
    @brief Custom object to hold a simulation input variable data
    '''
    
    def __init__(self, name=None, description=None, default=None,
                 bounds=None, values=None, units=None, logger=None):
        '''
        @param name  (Opt.) Printing name of the variable
        @param description (Opt.) A description for the  circuit
        @param default (Opt.) A default variable value
        @param bounds (Opt.) The bounds of the variable, [lower, upper]
        @param values (Opt.) Assign values to scan
        @param units (Opt.) units of the variable
        @param logger (Opt.) Custom logger object
        '''
        SimulationVariable.__init__(self, name=name, units=units, logger=logger)
        
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
        @brief set a description for this variable.
        @param description 
        @details This will be utilised in extended plotting functionality
        '''
        self.description = description
        
    def getDescription(self):
        '''
        @brief return the description
        @return str
        '''
        return self.description

    def setDefault(self, default):
        '''
        @brief sets the default value of the variable.
        @param default A float value
        @details Must be assignable to a float, otherwise nothing is done
        '''
        try:
            self.default = float(default)
        except:
            pass
    def getDefault(self):
        
        '''
        @brief return the default value
        @return float
        '''
        
        return self.default
    
    def setBounds(self, *args):
        '''
        @brief sets the bounds to a variable
        @param args Can either be a set of (lower_bound, upper_bound) arguments
        or a single list of [lower, upper] bounds values.
        @details Can accept either a list(or numpy array) single input, or a lower_bound, upper_bound argument pair
        @throw SimulationInputVariableError If there is an error assigning the arguments to floats
        '''
        if len(args) > 1:
            #lower_bound, upper_bound pair
            try:
                lower = float(bounds)
                upper = float(arg[0])
            except Exception, msg:
                self.logger.error("Exception raised while converting bounds. %s"%(str(args)))
                raise SimulationInputVariableError("Exception raised while converting bounds. %s"%(str(args)))
            
        else:
            
            bounds = args[0]
            if bounds:
                try:
                
                    lower = float(bounds[0])
                    upper = float(bounds[1])
                except:
                    self.logger.error("Something strange happening with the bounds: %s"%(str(bounds)))
                    raise SimulationVariableError("Something strange happened with the bounds conversion")
            else:
                lower  = upper = 0.0
            #self.logger.error("Exception raised while converting bounds. %s"%(str(args)))
            #raise SimulationInputVariableError("Exception raised while converting bounds. %s"%(str(args)))
        
        
        self.bounds = np.array([lower, upper])
       
    def getBounds(self):
        '''
        @brief returns the current bounds of the variable
        @return list
        '''
        return self.bounds
    
    def setValues(self, values):
        '''
        @brief Sets the variable values
        @param values A list of the values to assign
        @details
        if input argument is a list, then a numpy array will be created in its place
        '''
        if isinstance(values, (list, np.ndarray)):
            
            self.values = np.array(values)
            

        
    def getValues(self):
        '''
        @brief gets the stored values for this variable 
        @return list
        '''
        return self.values
    
    def setValuesFromBounds(self, length=None, spacing='lin'):
        '''
        @brief sets the values of the variable from the saved bounds, the array length,
        and the spacing type (log or lin) to use.
        @param length (Opt.) The array length to create.  Default is set in utils.config.spice_config module
        @param spacing (Opt.) The spacing type to use.  Either 'lin'(Default) or 'log'
        '''
        if not length:
            length = config.DEFAULT_ARRAY_LENGTH
        
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
        @brief sets the bounds from a values array
        @return list new bounds assigned
        '''
        
        lower = min(self.getValues())
        upper = max(self.getValues())
        
        self.setBounds(lower, upper)
        
        return self.getBounds()
    
    @classmethod
    def createFromDict(cls, values_dict):
        '''
        @brief returns a new instance from a dictionary of 
        @param cls The class to instantiate
        @param values_dict A dict of values to pass to the cls
        @return spice.simulation.variable.SimulationVariable A newly instantiated SimulationVariable
        '''
        return cls(**values_dict)
    
    #TODO: ???  Create from config file classmethod ???