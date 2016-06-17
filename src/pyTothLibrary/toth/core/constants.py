class Sections:
    NETWORK = 'network'
    PATH = 'path'
    GENOME = 'genome'
    FILE = 'file'

class Network:
    HOST = 'host'
    PORT = 'port'

class Path:
    DATASETS = 'datasets'
    DS_SPLIT = 'ds_split'
    LOGS = 'logs'
    KMER_INDEX = 'kmer_index'

class File:
    REFERENCE = 'reference'
    READS = 'reads'

class Genome:
    READ_SIDE_LENGTH = 'read_side_length'
    MIN_GAP = 'min_gap'
    MAX_GAP = 'max_gap'
    SPLIT_REF_PAGING = 'split_ref_paging'
    SPLIT_READ_LINES = 'split_read_lines'
    KMER_REF = 'kmer_ref'
    KMER_VECT_PAGING = 'kmer_vect_paging'

class Status:
    AVAILABLE = 'available'
    LOCKED = 'locked'
    ERROR = 'error'

class Pair_Side:
    LEFT = 'left'
    RIGHT = 'right'

class Pair_Direction:
    STRAIGHTFORWARD = 'straightforward'
    REVERSE = 'reverse'

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