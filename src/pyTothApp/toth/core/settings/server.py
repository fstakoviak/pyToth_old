import toth.core.collection
import toth.core.benchmark
import uuid

def init():
   
    global server_id
    global server_port
    global secondary_server_list
    global node_list
    global task_list
    global server_timer
    global keep_going
    global background_execution_interval
    global node_refresh_timeout
    global is_primary
    global server_state

    server_id = str(uuid.uuid1())
    server_port = 8080
    secondary_server_list = []
    node_list = toth.core.collection.NodeList()
    task_list = toth.core.collection.TaskList()
    server_timer = toth.core.benchmark.Timer()
    keep_going = True
    background_execution_interval = 10
    node_refresh_timeout = 60
    is_primary = False
    server_state = toth.core.constants.Node_State.RUNNING
