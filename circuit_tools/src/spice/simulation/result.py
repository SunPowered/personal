'''
@package spice.simulation.result
@file spice/simulation/result.py
@author timvb
@brief Module containing the SimulationResult object
'''
import os

import numpy as np


import spice.spice_read

from spice.simulation.variable import getSpiceFriendlyName

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
    
    def __init__(self, sim_type=None, variables=None, output_vectors=None, raw_file=None):
        '''
        @brief A Result file must be created before the simulation is run.  
        It is used by the simulator to track which data sets to track
        @param sim_type (Opt) The simulation type to run
        @param variables A list of variables to track
        @param output_vectors A list of vector names to save
        @param raw_file the raw file to track
        @todo Sim Types will end up being subclassed, remove the attribute and set/get methods
        '''   
        
        #TODO: remove
        #self.sim_type = sim_type
        
        self.variables = variables
        
        #Init output vectors
        self.output_vectors = []
        self.addOutputVectors(output_vectors)
          
        #Init raw_file
        self.raw_file = raw_file
        self.plots = {}
        
    #TODO: Sim Types will end up being subclassed, remove the attribute and set/get methods
    
    def getOutputVectors(self):
        '''
        @return a list of current output vector names
        '''
        return self.output_vectors
    
    
    def addOutputVector(self, vector_name):
        '''
        @brief Adds a new output vector to the result.  The vector is also
        available as a class attribute
        @param vector a str of a vector name
        '''
        vector_name = getSpiceFriendlyName(vector_name)
        setattr(self, vector_name, np.array([]))
        self.output_vectors.append(vector_name)
    
    
    def addOutputVectors(self, vectors):
        '''
        adds a list of output vectors to the result object
        '''
        if not vectors:
            return
        for vec in vectors:
            self.addOutputVector(vec)
                
                
    def appendToOutputVector(self, vector_name, value):
        '''
        @brief appends a value to an output vector
        '''
        if hasattr(self, vector_name):
            setattr(self, vector_name, getattr(self, vector_name).append(value))
    
    
    def setOutputVector(self, vector_name, values):
        if hasattr(self, vector_name):
            setattr(self, vector_name, values)
            
    """
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
    """
    
    def setRawFile(self, raw_file_path):
        '''
        @brief sets a raw file path to use for a simulation.  
        @param raw_file_path The file path to the raw file
        
        '''
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
        @throw SimulationResultError If file does not exist 
        
        The saved value is read by default
        '''
        
        raw_file_path = raw_file_path or self.getRawFile()
        if not os.path.isfile(raw_file_path):
            raise SimulationResultError("Raw File not found: %s"%(raw_file_path))
        spice_data = spice.spice_read.SpiceRead(raw_file_path).getPlots()
        
        
        for plot in spice_data:
            #Init new plot
            curplot = self.plots[plot.plotname] = {}
            
            #Handle scale vector
            scale_vector = plot.getScaleVector()
            curplot['scale'] = scale_vector.getData()
            self.setOutputVector(scale_vector.name, scale_vector.getData())

            #Handle all vectors in plot
            for vec in plot.getDataVectors():
                vec_name = getSpiceFriendlyName(vec.name)
                if vec_name in self.getOutputVectors():
                    #add to current plot
                    curplot[vec_name] = vec.getData()
                    self.setOutputVector(vec_name, vec.getData())
        #Search for output vectors in the data plot


        #TODO: append spice data to save_vectors ...
        # Raw files should have single values plots in the first plot
        # time, frequency vectors in a plot should be understood