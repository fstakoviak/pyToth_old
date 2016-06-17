class Network:
    HOST = 'host'
    PORT = 'port'

class Request_Type:
    CREATE_SESSION = 'create_session'
    REGULAR_MESSAGE = 'regular_message'
    KEEP_ALIVE = 'keep_alive'
    GET_TASK = 'get_task'
    FINISH_TASK = 'finish_task'
    TEST_CONNECTION = 'test_connection'
    GET_SECONDARY_SERVER_LIST = 'get_secondary_server_list'
    GET_TASK_SPLIT = 'get_task_split'

class Node_State:
    RUNNING = 'running'
    LISTENING = 'listening'
    UPDATING = 'updating'

class Error_Type:
    CONNECTION_ERROR = 'connection_error'