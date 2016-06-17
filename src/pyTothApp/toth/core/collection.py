import toth.core
from toth.core import io, constants, network
import os
import math
import operator
import random
import datetime

class NodeList:

    def __init__(self):
        self.__node_list = dict()
        self.__node_ids = []

    def create(self):

        node = network.Node()
        self.__node_list[node.get_id()] = node
        self.__node_ids.append(node.get_id())

        return node

    def get(self, node_id):

        if (self.__node_list.has_key(node_id)):
            return self.__node_list[node_id]    
        
        return None

    def index(self, node_id):

        if (node_id in self.__node_ids):
            return self.__node_ids.index(node_id)

        return -1

    def count(self):
        return len(self.__node_ids)

    def remove(self, node_id):

        if (self.__node_list.has_key(node_id)):
            self.__node_list.pop(node_id)

    def to_string(self):

        l_str = ''

        l_str += 'Count = %s\n' % len(self.__node_ids)

        for k in self.__node_list.iterkeys():
            l_str += self.__node_list[k].to_string() + '\n'

        l_str = l_str[:-1]

        return l_str

    def refresh(self, time_out):
        to_delete = []

        for k in self.__node_list.iterkeys():

            if (datetime.datetime.now() > self.__node_list[k].get_last_contact_datetime() + datetime.timedelta(0, time_out)):
                to_delete.append(k)

        for k in to_delete:
            self.__node_list.pop(k)
            self.__node_ids.remove(k)

class TaskList:
    def __init__(self):
        self.__task_list = []
        self.__task_queue = []
        self.__task_running = []
        self.__task_path = io.Path('./data/tasks/server/%s' % toth.core.settings.server.server_id)
        self.__task_path.ensure_exists()
        self.__task_path.delete_contents()

    def __generate_id(self):

        if len(self.__task_list) == 0:
            return 1

        return max(self.__task_list) + 1

    def add(self, task):
        task_id = self.__generate_id()
        task.set_id(task_id)
        self.__task_list.append(task_id)

        self.__save_task(task)

    def __save_task(self, task):      
        
        t_file = io.File(self.__task_path.get_dir_path(), '%s' % task.get_id())
        t_file.add('data', task.to_string())

        t_file.save()

    def count(self):
        return len(self.__task_list)

    def exists(self, task_id):
        t_file = io.File(self.__task_path.get_dir_path(), '%s' % task_id)

        return t_file.exists()


    def get(self, task_id):

        t_file = io.File(self.__task_path.get_dir_path(), '%s' % task_id)

        if t_file.exists():
            t_file.load_as_fasta([])
            t_str = t_file.get('data')[0]
            
            task = toth.application.Task()
            task.from_string(t_str)

            return task

        return None;

    def get_running_to_string(self):
        t_str = ''

        for x in self.__task_running:
            t_str += '[%s] :: [%s] \n' % (x[1], x[0])

        return t_str[:-1]

    def start_task(self, node_id):
        task_id = 0

        if len(self.__task_queue) > 0:
            task_id = self.__task_queue.pop(0)
            self.__task_running.append([task_id, node_id])

        if (task_id > 0):
            return self.get(task_id)

        return toth.core.application.Task()

    def finish_task(self, task_id, output):

        try:
            t_index = [x[0] for x in self.__task_running].index(task_id)
            self.__task_running.pop(t_index)
        except:
            pass

    def split(self, number_nodes, node_index):

        index_list = toth.core.application.Util.get_split_redundancy(self.count(), number_nodes, node_index)
        
        r_list = []

        for i in index_list:
            task_id = self.__task_list[i]    
            task = self.get(task_id)

            r_list.append(task.to_string())

        return r_list;


    def create_test_set(self, num_tasks):

        for i in range(num_tasks):

            t = toth.core.application.Task()

            method_number = random.randint(1, 3)

            if (method_number == 1):
                t.set_method('sum')
                t.add_parameter('num1', random.randint(0, 1000))
                t.add_parameter('num2', random.randint(0, 1000))
            elif (method_number == 2):
                t.set_method('divide')
                t.add_parameter('num1', random.randint(0, 1000))
                t.add_parameter('num2', random.randint(0, 1000))
            elif (method_number == 3):
                t.set_method('power')
                t.add_parameter('base', random.randint(0, 50))
                t.add_parameter('exponent', random.randint(0, 20))
            elif (method_number == 4):
                t.set_method('replace_text')
                t.add_parameter('search_for', '-')
                t.add_parameter('replace_to', ' ')
                t.add_parameter('size', random.randint(0, 50))
                t.set_dataset('Lorem-ipsum-dolor-sit-amet,-consectetur-adipiscing-elit.-Maecenas-aliquet-urna-eu-efficitur-ornare.-Praesent-sed-nunc-nunc.-Phasellus-nec-mattis-est,-vitae-scelerisque-justo.-Aenean-accumsan-mauris-ante,-eget-interdum-risus-euismod-ut.-Duis-egestas-tempus-arcu.-Phasellus-facilisis-semper-laoreet.-Mauris-hendrerit-ex-vel-nisi-pulvinar-rutrum.')

            self.add(t)
            self.__task_queue.append(t.get_id())

class TaskListLight:

    def __init__(self):
        self.__task_list = []
        self.__task_path = None

    def build_path(self):
        self.__task_path = io.Path('./data/tasks/client/%s' % toth.core.settings.client.node_id)
        self.__task_path.ensure_exists()
        self.__task_path.delete_contents()

    def add(self, task):
        self.__task_list.append(task.get_id())
        self.__save_task(task)

    def __save_task(self, task):      

        t_file = io.File(self.__task_path.get_dir_path(), '%s' % task.get_id())
        t_file.add('data', task.to_string())

        t_file.save()

    def exists(self, task_id):
        t_file = io.File(self.__task_path.get_dir_path(), '%s' % task_id)

        return t_file.exists()

    def count(self):
        return len(self.__task_list)


    def get(self, task_id):

        t_file = io.File(self.__task_path.get_dir_path(), '%s' % task_id)

        if t_file.exists():
            t_file.load_as_fasta([])
            t_str = t_file.get('data')[0]
            
            task = toth.application.Task()
            task.from_string(t_str)

            return task

        return None;

    def get_ids(self):
        return self.__task_list

    def remove(self, task_id):
         t_file = io.File(self.__task_path.get_dir_path(), '%s' % task_id)
         t_file.remove()
         self.__task_list.remove(task_id)

    def clear(self):

        for task_id in self.__task_list:
            t_file = io.File(self.__task_path.get_dir_path(), '%s' % task_id)
            t_file.remove()

        self.__task_list = []


    def refresh(self, task_list):

        self.clear()

        for task_str in task_list:    
            
            task = toth.core.application.Task()
            task.from_string(task_str)

            self.add(task)



            
