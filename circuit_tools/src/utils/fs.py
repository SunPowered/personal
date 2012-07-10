'''
Created on 2012-07-08

@author: timvb

utils.fs.py  - A local file system utilities module
'''
import os

def switchWDFromFilePath(file_path):
    '''
    gets the directory name of the file path, changes the current working directory to here
    
    returns the new cwd
    '''
    try:
        dir_name = os.path.dirname(file_path)
        os.chdir(dir_name)
    except:
        return None
    else:
        return os.getcwd()
