from toth.core import network

def main():

    n = network.Server(is_primary = True)
    n.start()


if __name__ == "__main__":
    main()