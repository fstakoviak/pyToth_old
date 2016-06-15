import toth.core.collection
import toth.core.benchmark

def init():
    global node_list
    global task_list
    global server_timer

    node_list = toth.core.collection.NodeList()
    task_list = toth.core.collection.TaskList()
    server_timer = toth.core.benchmark.Timer()
