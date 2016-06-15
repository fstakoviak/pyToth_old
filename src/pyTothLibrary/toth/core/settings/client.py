import toth

def init():

    global last_message
    global keep_alive_interval
    global task_list_light
    global node_id
    
    node_id = ''
    last_message = 0
    keep_alive_interval = 10
    task_list_light = toth.core.collection.TaskListLight()