import toth

def init():

    global primary_server_address
    global primary_server_port
    global client_server_port
    global secondary_server_list
    global current_server
    global task_list_light
    global node_id
    global node_address
    global keep_going
    global connection_attemptive_number
    global connection_attemptive_interval
    global background_execution_interval
    
    primary_server_address = '127.0.0.1'
    primary_server_port = 8080
    client_server_port = 8888
    secondary_server_list = []
    current_server = 0
    node_id = ''
    task_list_light = toth.core.collection.TaskListLight()
    node_address = ''
    keep_going = True
    connection_attemptive_number = 5
    connection_attemptive_interval = 5
    background_execution_interval = 30