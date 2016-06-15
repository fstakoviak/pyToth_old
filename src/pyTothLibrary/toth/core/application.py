from toth.core import constants
import toth.core.io
import ConfigParser
import urllib2
import StringIO
import os
from itertools import product
import json
import math

#class Config:
#    """Application set up class"""

#    def __init__(self, path):
#        """Create an instance of the Config class
#        Attributes:
#            path (str): path to the config file, it can be an url or physical path
#        """

#        self.__config = ConfigParser.ConfigParser()
        
#        if (path.startswith('http')):            
#            res = urllib2.urlopen(path)
#            inifile_text = res.read()

#            inifile = StringIO.StringIO(inifile_text)
#            inifile.seek(0)
#            self.__config.readfp(inifile)
#        else:
#            self.__config.read(path)

#    def get_value(self, section, option):
#        """Get a value of an option from a section of the config file
#        Attributes
#            section: section of the config file
#            option: option of the config file
#        Returns:
#            str: the corresponding value
#        """
#        return self.__config.get(section, option)


class Task:
    def __init__(self):
        self.__id = 0
        self.__method = ''
        self.__parameters = dict()
        self.__dataset = ''

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_method(self):
        return self.__method

    def set_method(self, method):
        self.__method = method

    def get_parameter(self, param_name):
        if (self.__parameters.has_key(param_name)):
            return self.__parameters[param_name]

        return None

    def add_parameter(self, param_name, param_value):
        self.__parameters[param_name] = param_value

    def remove_parameter(self, param_name):
        if self.__parameters.has_key(param_name):
            self.__parameters.pop(param_name)

    def get_dataset(self):
        return self.__dataset

    def set_dataset(self, dataset):
        self.__dataset = dataset

    def to_string(self):
        return json.dumps(self.__dict__)

    def from_string(self, task_str):
        jsonObj = json.loads(task_str)

        self.__id = jsonObj['_Task__id']
        self.__method = jsonObj['_Task__method']

        self.__dataset = jsonObj['_Task__dataset']

        for p in jsonObj['_Task__parameters']:
            self.__parameters[p] = jsonObj['_Task__parameters'][p]

    def to_string_console(self):

        t_str = ''
        t_str += '[Id] = %s \n' % self.__id
        t_str += '[Method] = %s \n' % self.__method
        t_str += '[Parameters] = %s \n' % json.dumps(self.__parameters)
        t_str += '[Dataset] = %s' % self.__dataset

        return t_str

class Util:
    
    def __init(self):
        pass

    @staticmethod
    def get_split_redundancy(list_length, number_of_splits, split_index):
        
        v_split = range(0, list_length)

        if (number_of_splits == 1):
            return v_split

        gap_length = (number_of_splits if number_of_splits < list_length else list_length) - 2

        r_factor = split_index + gap_length
        l_factor = r_factor - list_length 

        left_part = v_split[max(l_factor, 0):max(split_index, l_factor + split_index - 1)] if split_index > 0 else []
        right_part = v_split[r_factor:] if r_factor < list_length else []
        
        return_split = []
        return_split.extend(left_part)
        return_split.extend(right_part)

        return return_split
