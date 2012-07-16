'''
@package utils.fs
@author timvb
@file utils/fs.py
@brief Project filesystem utilities module
'''
import os

def switchWDFromFilePath(file_path):
    '''
    @brief Changes the current working directory to that of the given file
    @param file_path
    @return The new cwd
    '''
    try:
        dir_name = os.path.dirname(file_path)
        os.chdir(dir_name)
    except:
        return None
    else:
        return os.getcwd()


def waitForFile(file_path, interval=None, max_retries=None):
    import time
    '''
    @brief waits for a file to exist, retrying a number of times before raising an error
    @param interval The sleep time interval to wait before retry
    @param max_retry Maximum number of times to retry before failing
    @return bool True if file currently exists, False if retries maxed out 
    '''
    interval = interval or 1
    max_retries = max_retries or 3
    
    count = 0
    while not os.path.isfile(file_path):
        if count >= max_retries:
            return False
        time.sleep(interval)
        count += 1
    return True