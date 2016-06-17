import SocketServer
import threading
import socket
import time
import datetime
import platform
from toth.core import io, constants, settings, application
import uuid
import thread

class Client:

    
    def __init__(self, host = None, port = None):
       
        settings.client.init()

        if (host is not None):
            self.__address = host
            self.__port = port
        else:
            self.__address = settings.client.primary_server_address
            self.__port = settings.client.primary_server_port


###########################################################################

    def start(self):
         thread.start_new_thread(self.__background_execution, ())
        
    def stop(self):
        settings.client.keep_going = False

    def __background_execution(self):
        while (settings.client.keep_going):
            try:
                if (settings.client.node_id == ''):
                    self.create_session()

                self.keep_alive()
                self.get_task_split()
                self.get_secondary_server_list()

            except ValueError as err:
                if (err.args[0] == constants.Error_Type.CONNECTION_ERROR):
                    self.__change_server()
                else:
                    pass

            time.sleep(settings.client.background_execution_interval)

    def __change_server(self):
        print 'error'
        pass

###########################################################################

    def get_package(self, type):
        p_send = io.Package(type, settings.client.node_id)
        return p_send

    def create_session(self):

        p_send = self.get_package(constants.Request_Type.CREATE_SESSION)
        p_received = self.send(p_send)

        settings.client.node_id = p_received.get("data")[0]
        settings.client.node_address = p_received.get("data")[1]

        settings.client.task_list_light.build_path()


    def keep_alive(self):
         p_send = self.get_package(constants.Request_Type.KEEP_ALIVE)
         p_received = self.send(p_send)
         
    def get_task_split(self):

        p_send = self.get_package(constants.Request_Type.GET_TASK_SPLIT)
        p_send.add('data', '')

        p_received = self.send(p_send)

        data_received = p_received.get('data')

        settings.client.task_list_light.refresh(data_received)

    def get_secondary_server_list(self):
        
        p_send = self.get_package(constants.Request_Type.GET_SECONDARY_SERVER_LIST)

        p_received = self.send(p_send)

        data_received = p_received.get('data')

        if (len(data_received) == 0):
            settings.client.secondary_server_list = []
        else:
            settings.client.secondary_server_list = data_received

        print data_received
        


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

    def try_income_connection(self, address, port):

        p_send = self.get_package(constants.Request_Type.TEST_CONNECTION)
        p_send.add('data', address)
        p_send.add('data', port)

        p_received = self.send(p_send)

        return p_received.get('data')[0]

###########################################################################

    def send(self, package):

        message_to_send = package.to_string()
        message_received = io.Package('', '')

        connection_succeed = False

        count = 0

        while (count < settings.client.connection_attemptive_number) and (not connection_succeed):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect to server and send data
                sock.connect((self.__address, self.__port))
                sock.sendall(message_to_send)

                # Receive data from the server and shut down
                data = sock.recv(1024000)


                message_received.from_string(data)

                connection_succeed = True
            except:
                print 'Connection Failed! Trying again'
                count = count + 1
                time.sleep(settings.client.connection_attemptive_interval)

            finally:
                sock.close()

        if (connection_succeed):
            return message_received
        else:
            raise ValueError(constants.Error_Type.CONNECTION_ERROR)

###########################################################################

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        data = self.request.recv(1024)
        
        if (data == ''):
            return

        p_received = io.Package('', '')
        p_received.from_string(data)
        
        cur_thread = threading.current_thread()
        p_send = self.process(p_received, self.client_address[0])

        response = p_send.to_string()

        self.request.sendall(response)

    def get_package(self, type):
        p_send = io.Package(type, '')
        return p_send

###########################################################################

    def process(self, p_received, client_address):

        p_send = None

        type = p_received.get_type()

        node_id = p_received.get_node_id()

        if (type == constants.Request_Type.CREATE_SESSION):

            new_id = settings.server.node_list.create().get_id()

            p_send = self.get_package(constants.Request_Type.CREATE_SESSION)
            p_send.add('data', new_id)
            p_send.add('data', client_address)

        elif (type == constants.Request_Type.KEEP_ALIVE):
            
            node = settings.server.node_list.get(node_id)

            if (node == None):
                p_send = self.get_package(constants.Request_Type.KEEP_ALIVE)
            else:

                node.keep_alive()

                p_send = self.get_package(constants.Request_Type.KEEP_ALIVE)
                p_send.add('data', settings.server.server_state)
                
        elif (type == constants.Request_Type.GET_TASK):

            new_task = settings.server.task_list.start_task(node_id)

            p_send = self.get_package(constants.Request_Type.GET_TASK)
            p_send.add('data', new_task.to_string())

        elif (type == constants.Request_Type.FINISH_TASK):

            task_id = int(p_received.get('data')[0])
            output = p_received.get('data')[1]

            settings.server.task_list.finish_task(task_id, output)

            p_send = self.get_package(constants.Request_Type.GET_TASK)

        elif (type == constants.Request_Type.GET_TASK_SPLIT):

            p_send = self.get_package(constants.Request_Type.GET_TASK_SPLIT)

            t_split = settings.server.task_list.split(settings.server.node_list.count(), settings.server.node_list.index(node_id))

            for t_str in t_split:
                p_send.add('data', t_str)

        elif (type == constants.Request_Type.TEST_CONNECTION):
            
            address = p_received.get('data')[0]
            port = p_received.get('data')[1]

            is_open = self.check_is_open(address, port)

            if is_open:
                settings.server.secondary_server_list.append('%s:%s' % (address, port))

            p_send = self.get_package(constants.Request_Type.TEST_CONNECTION)
            p_send.add('data', str(is_open))

        elif (type == constants.Request_Type.GET_SECONDARY_SERVER_LIST):

            p_send = self.get_package(constants.Request_Type.GET_SECONDARY_SERVER_LIST)

            for s in settings.server.secondary_server_list:
                p_send.add('data', s)

            if (len(p_send.get('data')) == 0):
                p_send.add('data', '')


        return p_send

###########################################################################

    def check_is_open(self, address, port):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        connection_succeed = False

        try:
            s.settimeout(10)
            s.connect((address, int(port)))
            
            connection_succeed = True
        except:
            pass
        finally:
            s.close()

        return connection_succeed

###########################################################################

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

###########################################################################

class Server:

    def __init__(self, port = None, is_primary = False):
        
        settings.server.init()

        self.__address = '0.0.0.0'

        if (port is not None):
            self.__port = port
        else:
            self.__port = settings.server.server_port

        settings.server.is_primary = is_primary

        if (settings.server.is_primary):
            settings.server.task_list.create_test_set(10)

        settings.server.server_timer.start()


    def start(self):

        server = ThreadedTCPServer((self.__address, self.__port), ThreadedTCPRequestHandler)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)

        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        thread.start_new_thread(self.__background_execution, ())

        if (settings.server.is_primary):
            self.__show_menu()
        else:
            print "Secondary server started"


    def stop(self):
        settings.server.keep_going = False

        if (settings.server.is_primary):
            pass
        else:
            print "Secondary server stopped"

    def __show_menu(self):

        while(settings.server.keep_going):
            m_option = self.get_menu()
            settings.server.keep_going = (m_option != '0')

            if (m_option == '1'):
                self.option_server_state()
            elif (m_option == '2'):
                self.option_active_client()
            elif (m_option == '3'):
                self.option_running_task()
            elif (m_option == '4'):
                self.option_secondary_server()

    def __background_execution(self):

        while(settings.server.keep_going):
            try:
                settings.server.node_list.refresh(time_out)
            except:
                pass

            time.sleep(settings.server.background_execution_interval)

###########################################################################

    def get_menu(self):

        menu_str = ''
        menu_str += '======= MENU ======= \n'
        menu_str += '\n'
        menu_str += '[1] Server state \n'
        menu_str += '[2] List of active clients \n'
        menu_str += '[3] List of running tasks \n'
        menu_str += '[4] List of secondary servers \n'

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
        content += '   [Host] - %s:%s \n' % (self.__address, self.__port)
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

    def option_secondary_server(self):

        title = 'List of Secondary Servers'

        t_secondar_server = 'Count = %s\n' % len(settings.server.secondary_server_list)
        
        for s in settings.server.secondary_server_list:
            t_secondar_server += '%s\n' % s


        content = t_secondar_server[:-1]

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
