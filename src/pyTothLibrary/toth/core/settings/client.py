import toth

def init():

    global client_nick_name
    global last_message
    global keep_alive_interval
    global task_list_light

    
    client_nick_name = ''
    last_message = 0
    keep_alive_interval = 30
    task_list_light = toth.core.collection.TaskListLight()