import datetime

class Timer:
    """Class to measure time of a procedure"""

    def __init__(self):
        """Create an instance of the Timer class"""
        self.__start = None
        self.__end = None
        self.__on = False

    def start(self):
        """Start the timer"""
        self.__start = datetime.datetime.now()
        self.__end = None
        self.__on = True

    def stop(self):
        """Stop the timer"""
        self.__end = datetime.datetime.now()
        self.__on = False

    def get_time(self):
        """Get the partial time
        Returns:
            time: the difference of the current time and the start time
        """
        diff = None
        if (self.__on):
            diff = datetime.datetime.now() - self.__start
        else:
            diff = self.__end - self.__start

        return diff

    def print_time(self, c_message):
        """Get a string the partial time and custom message
        Attributes:
            c_message (str): the custom message
        Returns
            str: get_time() + custom message
        """
        print '== %s: %s' % (self.get_time(), c_message)