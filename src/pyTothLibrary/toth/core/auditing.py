from toth.core import io
from toth.core import benchmark
from toth.core import constants

class Log(io.File):
    """Application logging class"""

    def __init__(self, name, config):
        """Create an instance of the Log class
        Attributes:
            name (str): name of the log
            config (toth.application.Config): config object
        """
        self.__config = config
        self.__timer = benchmark.Timer()
        self.__log_path = self.__config.get_value(constants.Sections.PATH, constants.Path.LOGS)

        f = io.File.__init__(self, self.__log_path, name + '.txt')


    def start(self):
        self.__timer.start()

    def stop(self):
        self.__timer.stop()

    def record_time(self, description):
        self.add(description, self.__timer.get_time())

