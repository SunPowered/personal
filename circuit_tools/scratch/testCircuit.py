'''
Created on 2012-07-06

@author: timvb
'''

from utils import log

from circuit import Circuit

test_file = '../data/schmitt.trigger.sch'

logger = log.StreamLogger('testCircuit')

c = Circuit(test_file, logger=logger)


print c.parseVariables()
