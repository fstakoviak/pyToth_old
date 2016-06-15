from toth.core import network

def main():

    #url = 'http://fstakoviak.bol.ucla.edu/bioinformatics/config/server.ini'

    #c = application.Config(url)

    #host = c.get_value(constants.Sections.NETWORK, constants.Network.HOST)
    #port = int(c.get_value(constants.Sections.NETWORK, constants.Network.PORT))

    #server_name = raw_input('Type the name of the server: ')
    #server_port = raw_input('Type the port of the server: ')

    server_name = '0.0.0.0'
    server_port = 8080

    n = network.Server(server_name, int(server_port))
    n.start()

if __name__ == "__main__":
    main()