'''
Created on 2012-06-27

@author: timvb
'''
import os
import re
import string

class CircuitException(Exception):
    pass

class CircuitVariableException(CircuitException):
    pass

class Circuit(object):
    '''
    Class for a single electrical circuit.  To be used for file parsing and simulating with ngspice 
    '''


    def __init__(self, filename, name=None):
        '''
        Circuit class is a netlisted circuit.
        
        Currently being developed for spice simulation
        
        TODO: Extend for more netlisting schemes
        '''
        assert os.path.isfile(filename), "File does not exist: %s"%(filename)
        self.filename = filename
        
        #Create temp filename
        base, rest = os.path.split(self.filename)
        name, ext = os.path.splitext(rest)
        self.temp_filename = os.path.join(base, name + '.tmp' + ext)
        
        #If name is given, assign the circuit name to it, otherwise take it from the filename
        if name:
            self.name = name
        else:
            self.name = os.path.splitext(os.path.basename(self.filename))[0]
        
        
        self.variables = []
        self.variable_character = "$"
        self.variable_character_regex = r"\$"
        self.comment_character = "*"
        self.comment_character_regex = r"\*"
        
        #Compile pattern to look for any \$[a-zA-Z0-9] with no comment character at the beginning
        self.variable_pattern = r"^[^" + self.comment_character_regex + r"].*(" +self.variable_character_regex + r"\w+).*$"
        self.variable_re = re.compile(self.variable_pattern, re.MULTILINE)
        self.parse_variables()

    def set_name(self, name):
        self.name = name
        
    def get_name(self):
        return self.name
    
    def get_temp_filename(self):
        return self.temp_filename
    
    def get_variables(self):
        return self.variables
    def parse_variables(self):
        '''
        The idea is to parse the file and get a result of all
        variables that are included in the circuit file.
        
        These variables should be stored as a way to check allowed variable calls later
        @return: the number of variables parsed
        
        '''
        try:
            match  =  self.variable_re.findall(open(self.filename, 'r').read())
        except Exception, msg:
            print "Error in matching: %s"%(msg)
        else:
            self.variables = [m.replace(self.variable_character, "") for m in match]
            return len(self.variables)
    
    def get_num_variables(self):
        return len(self.get_variables())
    
    def run_interactive_spice(self):
        '''
        Run the circuit with ngspice in interactive mode
        '''
        os.system("ngspice %s"%(self.filename))    
        
    def run_circuit_batch(self, silent=False):
        '''
        Run the circuit with ngspice in batch mode.  
        
        The silent keyword switches the output to and from the console
        
        '''
        output_directs = ""
        if silent:
            output_directs = "1>/dev/null 2>/dev/null"
        os.system("ngspice -b %s %s"%(self.filename, output_directs))
        
    def get_template(self):
        '''
        Return a string template, ready for $- substitutions 
        '''
        return string.Template(open(self.filename, 'r').read())
    
    def insert_variables(self, variable_vector):
        '''
        Insert a vector into a template of the current circuit and save it to the temp file
        '''
        #Check validity of input arg
        if not isinstance(variable_vector, dict):
            raise CircuitVariableException("Circuit variables vector must be a dict")
        
        #Build the safe substitute variable dict
        var_dict = {}
        for v in self.get_variables():
            try:
                val = variable_vector[v]
            except KeyError:
                raise CircuitVariableException("Missing key from variables vector dict: %s"%(str(v)))
            else:
                var_dict[v] = val
        
        #Get template and substitute the variables
        template = self.get_template()
        
        
        #write to temp file
        self._write_data_to_temp_file(template.safe_substitute(var_dict))
        
    def _write_data_to_temp_file(self, data):
        open(self.get_temp_filename(), 'wt').write(data)
        