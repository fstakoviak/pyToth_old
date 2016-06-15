import SocketServer
import threading
import socket
import platform
import thread

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        
        data = self.request.recv(1024)
        
        cur_thread = threading.current_thread()

        is_open = check_is_open(data.split(':')[0], int(data.split(':')[1]))

        self.request.sendall(str(is_open))

def check_is_open(ip,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(10)
        s.connect((ip, int(port)))

        return True
    except:
        return False
    finally:
        s.close()

if __name__ == "__main__":

    server = ThreadedTCPServer(('0.0.0.0', 8080), ThreadedTCPRequestHandler)

    #ip, __port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    print 'RUNNING'

    while True:
        pass