'''
@package utils.log
@author timvb
@file utils/log.py
@brief Project logging utilities module
'''
import os

import logging

from utils import config

#Log variables
LOG_PATH = os.path.normpath(os.path.join(os.path.basename(__file__), os.pardir, os.pardir, 'log'))

#Set default log format here, should always be capable of being overridden
#_default_format = "[ %(levelname)s : %(name)s ] - %(message)s"
_default_format = "%(message)s"
#Default log level
if config.DEBUG:
    _default_level = logging.DEBUG
else:
    _default_level = logging.INFO
    
#Default logger

#Null Logger
def NullLogger():
    '''
    @brief returns a null logger instance
    @return logging.Logger Null Instance
    '''
    logger = logging.getLogger("Null")
    logger.setLevel(logging.DEBUG)
   
    handler = logging.NullHandler()
    logger.addHandler(handler)
    return logger



#Stream Logger
def StreamLogger(name, **kwargs):  
    '''
    @brief A logger to spit out to std
    @param name The name to set to the logger   
    @param kwargs @li <b>level</b> (Opt) Logging level to use
    @li <b>log_format</b> (Opt) Custom log message format string
    @li <b>print_format</b> (Opt) Boolean Prints the message format as a header at the start of 
    the log session
    @return logging.Logger instance with a given logger name and logging level 
    stream handler and default formatting.  
    
    @details
    Used for quick dev
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