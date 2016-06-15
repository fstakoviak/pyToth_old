import SocketServer
import threading
import socket
import time
import datetime
import platform
from toth.core import io, constants, settings, application, benchmark
import uuid
import thread

class Client:

    
    def __init__(self, host, port):

        self.__host = host
        self.__port = port
        self.__node_id = ''
        self.keep_going = True

        settings.client.init()

        self.create_session()

        settings.client.node_id = self.__node_id

        thread.start_new_thread(self.keep_alive, ())

    def get_node_id(self):
        return self.__node_id

###########################################################################

    def get_package(self, type):
        p_send = io.Package(type, self.__node_id)
        return p_send

    def create_session(self):

        p_send = self.get_package(constants.Request_Type.CREATE_SESSION)
        p_received = self.send(p_send)

        self.__node_id = p_received.get("data")[0]

    def keep_alive(self):

        while(True):
            print '.1'
            p_send = self.get_package(constants.Request_Type.KEEP_ALIVE)
            
            has_error = True

            if (settings.client.task_list_light.count() > 0):
                p_send.add('data', ','.join([str(n) for n in settings.client.task_list_light.get_ids()]))
            else:
                p_send.add('data', '')

            p_received = self.send(p_send)

            data_received = p_received.get('data')

            settings.client.task_list_light.refresh(data_received)

            time.sleep(30)

    def get_task(self):

        p_send = self.get_package(constants.Request_Type.GET_TASK)
        p_received = self.send(p_send)
        
        task = application.Task()
        
        task.from_string(p_received.get('data')[0])

        return task

    def finish_task(self, task_id, output):

        p_send = self.get_package(constants.Request_Type.FINISH_TASK)
        p_send.add('data', task_id)
        p_send.add('data', output)

        p_received = self.send(p_send)
        


###########################################################################

    def get_system_info(self):

        sys_info = io.Package('', '')

        sys_info.add('name', platform.node())
        sys_info.add('full-name', socket.getfqdn())
        sys_info.add('ip', socket.gethostbyname(socket.gethostname()))
        sys_info.add('system', platform.system())
        sys_info.add('machine', platform.machine())
        sys_info.add('version', platform.version())
        sys_info.add('platform', platform.platform())
        sys_info.add('processor', platform.processor())
        
        return sys_info

###########################################################################

    def send(self, package):

        message_to_send = package.to_string()
        message_received = io.Package('', '')

        connection_succeed = False

        while not connection_succeed:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect to server and send data
                sock.connect((self.__host, self.__port))
                sock.sendall(message_to_send)

                # Receive data from the server and shut down
                data = sock.recv(1024000)


                message_received.from_string(data)

                connection_succeed = True
            except:
                print 'Connection Failed! Trying again'
                time.sleep(5)

            finally:
                sock.close()

        return message_received
    
###########################################################################

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        data = self.request.recv(1024000)

        p_received = io.Package('', '')
        p_received.from_string(data)
        
        cur_thread = threading.current_thread()

        p_send = self.process(p_received)

        response = p_send.to_string()

        self.request.sendall(response)

    def get_package(self, type):
        p_send = io.Package(type, '')
        return p_send

    def process(self, p_received):

        p_send = None

        type = p_received.get_type()

        node_id = p_received.get_node_id()

        if (type == constants.Request_Type.CREATE_SESSION):

            new_id = settings.server.node_list.create().get_id()

            p_send = self.get_package(constants.Request_Type.CREATE_SESSION)
            p_send.add('data', new_id)

        elif (type == constants.Request_Type.KEEP_ALIVE):
            
            node = settings.server.node_list.get(node_id)

            if (node == None):
                p_send = self.get_package(constants.Request_Type.KEEP_ALIVE)
            else:

                node.keep_alive()

                p_send = self.get_package(constants.Request_Type.KEEP_ALIVE)

                t_split = settings.server.task_list.split(settings.server.node_list.count(), settings.server.node_list.index(node_id))

                print [node_id, len(t_split)]

                for t_str in t_split:
                    p_send.add('data', t_str)

                
        elif (type == constants.Request_Type.GET_TASK):

            new_task = settings.server.task_list.start_task(node_id)

            p_send = self.get_package(constants.Request_Type.GET_TASK)
            p_send.add('data', new_task.to_string())

        elif (type == constants.Request_Type.FINISH_TASK):

            task_id = int(p_received.get('data')[0])
            output = p_received.get('data')[1]

            settings.server.task_list.finish_task(task_id, output)

            p_send = self.get_package(constants.Request_Type.GET_TASK)

        return p_send

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

###########################################################################

class Server:

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.keep_going = True

        settings.server.init()
        settings.server.task_list.create_test_set(10)
        settings.server.server_timer.start()

        thread.start_new_thread(self.background_execution, ())

    def start(self):
        server = ThreadedTCPServer((self.__host, self.__port), ThreadedTCPRequestHandler)

        #ip, __port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        #print 'RUNNING: %s:%s' % (self.__host, self.__port)
        #print

        while(self.keep_going):

            m_option = self.get_menu()
            self.keep_going = (m_option != '0')

            if (m_option == '1'):
                self.option_server_state()
            elif (m_option == '2'):
                self.option_active_client()
            elif (m_option == '3'):
                self.option_running_task()


    def stop(self):
        self.keep_going = False

    def restart(self):
        self.stop()
        time.sleep(5)
        self.start()

    def background_execution(self):

        time_out = 10

        while(self.keep_going):
            try:
                settings.server.node_list.refresh(time_out)
            except:
                pass

            time.sleep(5)

    def get_menu(self):

        menu_str = ''
        menu_str += '======= MENU ======= \n'
        menu_str += '\n'
        menu_str += '[1] Server state \n'
        menu_str += '[2] List of active clients \n'
        menu_str += '[3] List of running tasks \n'

        menu_str += '\n'
        menu_str += '[0] Exit \n'
        menu_str += '\n'

        print menu_str

        m_option = raw_input('Select one option: ')

        return m_option

    def print_menu_option(self, title, content):

        print
        print
        print '======= %s =======' % title
        print
        print content
        print
        print ''.join(['=' for x in range (16 + len(title))]) #'============='
        print
        print

    def option_server_state(self):

        title = 'Server State'
        content = ''
        content += '   [Host] - %s:%s \n' % (self.__host, self.__port)
        content += '[Up Time] - %s' % settings.server.server_timer.get_time()

        self.print_menu_option(title, content)

    def option_active_client(self):

        title = 'List of Active Clients'

        node_list_str = settings.server.node_list.to_string()

        #content = node_list_str if len(node_list_str) > 0 else 'No active clients'
        content = node_list_str

        self.print_menu_option(title, content)

    def option_running_task(self):

        title = 'List of Running Task'

        t_running = settings.server.task_list.get_running_to_string()

        content = t_running if len(t_running) > 0 else 'No running tasks'

        self.print_menu_option(title, content)


###########################################################################

class Node:
    
    def __init__(self):
        self.__id = str(uuid.uuid1())
        self.__creation_datetime = datetime.datetime.now()
        self.__last_contact_datetime = datetime.datetime.now()

    def get_id(self):
        return self.__id

    def get_creation_datetime(self):
        return self.__creation_datetime

    def get_last_contact_datetime(self):
        return self.__last_contact_datetime

    def keep_alive(self):
        self.__last_contact_datetime = datetime.datetime.now()

    def to_string(self):
        n_str = '[%s] [%s] [%s]' % (self.__id, self.__creation_datetime, self.__last_contact_datetime)

        return n_str
