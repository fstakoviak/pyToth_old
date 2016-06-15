import socket
import sys
import datetime
import time
import math

from toth.core import network
from toth.core import io
from toth.core import application
from toth.core import constants
from toth.core import settings

def main():
    #url =
    #'http://fstakoviak.bol.ucla.edu/bioinformatics/config/server_10K.ini'

    #c = application.Config(url)
    #host = c.get_value(constants.Sections.NETWORK, constants.Network.HOST)
    #port = int(c.get_value(constants.Sections.NETWORK,
    #constants.Network.PORT))

    server_name = '127.0.0.1'
    server_port = 8080

    print '== Connecting =='
    time.sleep(1)

    n = network.Client(server_name, int(server_port))

    print '[Client_Id] %s' % n.get_node_id()
    print

    print '==== Requesting Tasks'
    print


    while(True):

        #task = n.get_task()

        print settings.client.task_list_light.get_ids()

        time.sleep(5)

        #n.keep_going = task.get_id() > 0

        #if (task.get_id() <= 0):
        #    time.sleep(1)
        #else:
        #    print '==== Task Received'
        #    print task.to_string_console()

        #    method_name = task.get_method()

        #    if (method_name == 'sum'):
        #        output = sum(task.get_parameter('num1'), task.get_parameter('num2'))
        #    elif (method_name == 'divide'):
        #        output = divide(task.get_parameter('num1'), task.get_parameter('num2'))
        #    elif (method_name == 'power'):
        #        output = divide(task.get_parameter('base'), task.get_parameter('exponent'))
        #    elif (method_name == 'replace_text'):
        #        output = replace_text(task.get_dataset(), task.get_parameter('search_for'), task.get_parameter('replace_to'), task.get_parameter('size'))

        #    time.sleep(2)

        #    print '[Output] %s' % output
        #    print '===== Task Completed'
        #    print

        #    n.finish_task(task.get_id(), output)

        #    time.sleep(3)
            
    print '== Execution completed =='

def sum(num1, num2):
    return num1 + num2

def divide(num1, num2):

    if (num2 == 0):
        num2 = 1

    return float(num1) / float(num2)

def power(base, exponent):

    if (exponent == 0):
        exponent = 1

    return math.pow(base, exponent)

def replace_text(text, search_for, replace_to, size):
    return text.replace(search_for, replace_to)[:size]

if __name__ == "__main__":
    main()
    

