'''
Created on 2012-07-06

@author: timvb

Project Wide log utilities
'''

import os

import logging

#Log variables
LOG_PATH = os.path.normpath(os.path.join(os.path.basename(__file__), os.pardir, os.pardir, 'log'))

#Set default log format here, should always be capable of being overridden
#_default_format = "[ %(levelname)s : %(name)s ] - %(message)s"
_default_format = "%(message)s"
#Default log level
_default_level = logging.DEBUG
#Default logger

#Null Logger
def NullLogger():
    '''
    returns a null logger instance
    '''
    logger = logging.getLogger("Null")
    logger.setLevel(logging.DEBUG)
    handler = logging.NullHandler()
    logger.addHandler(handler)
    return logger



#Stream Logger
def StreamLogger(name, **kwargs):  
    '''
    hey you!
    
    returns a logger instance with a given logger name and logging level 
    stream handler and default formatting.  Used for quick dev
    
    level=_default_level, log_format=_default_format, print_format=False):
    '''
    level = kwargs.get('level', _default_level)
    log_format = kwargs.get('log_format',_default_format)
    import sys
    #Init Logger with given name
    logger = logging.getLogger(name)
    #Set the logging level
    logger.setLevel(level)
    #init formatter
    formatter = logging.Formatter(log_format)
    #init stream handler to stdout
    handler = logging.StreamHandler(sys.__stdout__)
    handler.setFormatter(formatter)
    #Assign handler to logger
    logger.addHandler(handler)
    if kwargs.get('print_format',False):
        logger.info("Stream Log Handler to stdout")
        logger.info("Level: %s Format: %s"%(str(level), log_format))
    return logger

_default_logger = StreamLogger

def getDefaultLogger(name):
    return _default_logger(name)