class Fasta:
    """Class that represent the Fasta format"""

    def __init__(self):
        self.__content = dict()

    def is_empty(self):
        return len(self.__content) == 0

    def has_key(self, key):
        key = str(key)
        return self.__content.has_key(key)

    def add(self, key, value):
        key = str(key)
        if (not self.__content.has_key(key)):
            self.__content[key] = []
        self.__content[key].append(value)

    def get(self, key):
        key = str(key)
        if (self.__content.has_key(key)):
            return self.__content[key]
        else:
            return []

    def get_headsections(self):
        return self.__content.keys()

    def remove(self, key):
        key = str(key)
        del self.__content[key]

    def clear(self):
        self.__content.clear()

    def to_string(self):
        s_return = ''

        for key in self.__content:
            s_return += '>%s\n' % key

            for item in self.__content[key]:
                s_return += '%s\n' % item

        return s_return

    def from_string(self, content_string):
        
        current_key = 'no-content'

        for line in content_string.split('\n'):
            line = line.strip('\n').strip('\t').strip('\r').strip(' ')
            if (line.startswith('>')):
                current_key = line[1:]
                self.__content[current_key] = []
            else:
                self.__content[current_key].append(line)