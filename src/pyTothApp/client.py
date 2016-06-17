import socket
import sys
import datetime
import time
import math
import thread

from toth.core import network
from toth.core import io
from toth.core import application
from toth.core import constants
from toth.core import settings
from toth import samples

def main():
    
    c = network.Client()

    c.start()

    time.sleep(5)

    s = network.Server(port = settings.client.client_server_port)

    try:
        s.start()

        time.sleep(5)

        print 'Testing client server port'
    
        connection_succeed = c.try_income_connection(settings.client.node_address, settings.client.client_server_port)

        if connection_succeed:
            print 'Incoming connections succeeded'
        else:
            print 'Incoming connections failed'
            print 'Stopping secondary server'
            s.stop()
    except:
        s.stop()
        print 'Error creating client server'

    while(c.keep_alive):

        task = c.get_task()

        if (task.get_id() <= 0):
            time.sleep(1)
        else:
            print 'Task Received: %s' % task.get_id()

            method_name = task.get_method()

            if (method_name == 'sum'):
                output = samples.task.Methods.sum(task.get_parameter('num1'), task.get_parameter('num2'))
            elif (method_name == 'divide'):
                output = samples.task.Methods.divide(task.get_parameter('num1'), task.get_parameter('num2'))
            elif (method_name == 'power'):
                output = samples.task.Methods.divide(task.get_parameter('base'), task.get_parameter('exponent'))
            elif (method_name == 'replace_text'):
                output = samples.task.Methods.replace_text(task.get_dataset(), task.get_parameter('search_for'), task.get_parameter('replace_to'), task.get_parameter('size'))


            c.finish_task(task.get_id(), output)

            time.sleep(5)


if __name__ == "__main__":
    main()
    
