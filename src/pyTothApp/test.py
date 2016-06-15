import SocketServer
import threading
import socket
import platform
import thread

def main():
    pass

def send(address, port, message = ''):

    connection_succeed = False

    try:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to server and send data
        sock.connect((address, port))

        sock.sendall(message)
        
        # Receive data from the server and shut down
        data = sock.recv(1024)

        return data

    except:
        print 'Error - [%s:%s] - [%s]' % (address, port, message)

    finally:
        sock.close()

    return connection_succeed

if __name__ == "__main__":

    while True:
        address = raw_input('Enter the address: ')
        port = raw_input('Enter the port number: ')

        print send('164.67.232.129', 8080, '%s:%s' % (address, port))

        print