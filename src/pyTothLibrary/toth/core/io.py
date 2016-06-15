import os, os.path
import shutil
import datetime
from toth.core import formats, constants

class Package(formats.Fasta):

    def __init__(self, type, node_id):

        a = formats.Fasta.__init__(self)

        self.add('type', type)
        self.add('node_id', node_id)

        return a

    def get_type(self):
        p_type = self.get('type')[0]
        return p_type

    def get_node_id(self):
        n_id = self.get('node_id')[0]
        return n_id

    def print_console(self):
        print '[type]', self.get_type()
        print '[node_id]', self.get_node_id()
        print '[Time]', datetime.datetime.now()
        print

    
###################################################################

class Path():

    def __init__(self, dir_path):
        self.__dir_path = dir_path

    def get_dir_path(self):
        return self.__dir_path

    def delete_itself(self):
        if (self.exists()):
            shutil.rmtree(self.__dir_path)

    def delete_contents(self):
        self.delete_itself()
        self.create()

    def delete_file(self, file):
        os.remove(os.path.join(self.__dir_path, file))

    def create(self):
        os.makedirs(self.__dir_path)

    def create_sub(self, name):
        if not os.path.exists(os.path.join(self.__dir_path, name)):
            os.makedirs(os.path.join(self.__dir_path, name))

    def exists(self):
        return os.path.exists(self.__dir_path)

    def ensure_exists(self):
        if (not self.exists()):
            os.makedirs(self.__dir_path)

    def get_files(self):
        for _, _, files in os.walk(self.get_dir_path()):
            return files

    def get_sub_dir_obj(self, sub_dir):
        return Path(os.path.join(self.get_dir_path(), sub_dir))

###################################################################

class File(formats.Fasta):

    def __init__(self, dir_path, file_name_w_extension):
        self.__dir_path = dir_path
        self.__file_name_extension = file_name_w_extension
        self.__number_lines = 0
        self.__file_size = 0

        return formats.Fasta.__init__(self)

    def __file_exists_changed(self):
        has_file = self.exists()
        has_changed = False

        if (has_file):
            current_f_disk_size = self.get_size()
            has_changed = self.__file_size != current_f_disk_size

            if (has_changed):
                self.__file_size = current_f_disk_size
                self.__number_lines = 0

        return has_file, has_changed

    def get_complete_path(self):
        return os.path.join(self.__dir_path , self.__file_name_extension)

    def get_extension(self):
        return os.path.splitext(self.__file_name_extension)[1]

    def get_name(self):
        return os.path.splitext(self.__file_name_extension)[0]

    def exists(self):
        return os.path.exists(self.get_complete_path())

    def read_iterator(self, to_remove):
        with open(self.get_complete_path(), 'rU') as file_obj:
            for line in file_obj:
                for c in to_remove:
                    line = line.strip(c)
                yield False, line

            yield True, ''

    def load_as_fasta(self, to_remove):
        if (self.exists()):
            current_key = 'not-fasta'
            for _, line in self.read_iterator(to_remove):
                if (line.startswith('>')):
                    current_key = line.lstrip('>').replace('\n', '')
                else:
                    self.add(current_key, line)
            
    def save(self):
        self.__number_lines = 0
        with open(self.get_complete_path(), 'w') as file_obj:
            file_obj.write(self.to_string())

    def save_custom(self, custom_content):
        self.__number_lines = 0
        with open(self.get_complete_path(), 'w') as file_obj:
            file_obj.write(custom_content)

    def get_size(self):
        return os.path.getsize(self.get_complete_path())

    def get_number_lines(self):
        n_lines = 0

        if (self.is_empty()):
            has_file, has_changed = self.__file_exists_changed()
            if (has_file):
                if (has_changed):
                    with open(self.get_complete_path(), 'rU') as file_obj:
                        for line in file_obj:
                            n_lines += 1
                else:
                    return self.__number_lines
        else:
            for k in self.get_headsections():
                n_lines += len(self.get(k))

        self.__number_lines = n_lines

        return self.__number_lines

    def remove(self):
        if (self.exists()):
            os.remove(self.get_complete_path())

