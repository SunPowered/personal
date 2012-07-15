'''
@package spice.simulation.result
@file spice/simulation/result.py
@author timvb
@brief Module containing the SimulationResult object
'''
import os

import numpy as np

import spice.spice_read

class SimulationResultError(Exception):
    pass
     
class SimulationResult(object):
    
    _default_dependent_output_variable='time'
    
    '''
    @brief An object to store simulation results from many individual simulations.  
    
    @details
    It may need to be created and configured for each simulation run which is performed. 
    
    Should have the ability to read raw ngspice data and store relevant data persistently
    
    Also have the capability to plot?
    '''
    
    def __init__(self, sim_type=None, variables=None, save_vectors=None, raw_file=None):
        '''
        @brief A Result file must be created before the simulation is run.  
        It is used by the simulator to track which data sets to track
        @param sim_type (Opt) The simulation type to run
        @param variables A list of variables to track
        @param save_vectors A list of save vectors
        @param raw_file the raw file to track
        @todo Sim Types will end up being subclassed, remove the attribute and set/get methods
        '''   
        
        #TODO: remove
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
        
    #TODO: Sim Types will end up being subclassed, remove the attribute and set/get methods
    def setSimType(self, sim_type):
        '''
        sets the simulation type
        '''
        self.sim_type = sim_type    
    
    def getSimType(self):
        '''
        gets the sim type
        '''
        return self.sim_type
    
    def setRawFile(self, raw_file_path):
        '''
        @brief sets a raw file path to use for a simulation.  
        @param raw_file_path The file path to the raw file
        @throw SimulationResultError If file does not exist 
        '''
        if not os.path.isfile(raw_file_path):
            raise SimulationResultError("Raw File not found: %s"%(raw_file_path))
        self.raw_file = raw_file_path
        '''
        @todo try to read the raw file here?
        '''
        
    def getRawFile(self):
        '''
        @brief return the current raw file for reading
        '''
        return self.raw_file
    
    def readRawFile(self, raw_file_path=None):
        '''
        @brief reads a spice raw file and saves the relevant data
        @param raw_file_path An optional raw file path to read.
        The saved value is read by default
        '''
        raw_file_path = raw_file_path or self.getRawFile()
        
        spice_data = spice.spice_read.SpiceRead(raw_file_path).getPlots()
        
        #TODO: append spice data to save_vectors ...
        # Raw files should have single values plots in the first plot
        # time, frequency vectors in a plot should be understood