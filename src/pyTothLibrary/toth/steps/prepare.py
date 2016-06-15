from toth.core import io, genome, collection
from toth.core import formats, constants
import os, os.path
import math

class ReferenceFile:
    def __init__(self, config):
        self.__config = config

    ##############################################################
    #SPLIT REF_FILE
    ##############################################################

    def split(self):
        path_ds = self.__config.get_value(constants.Sections.PATH, constants.Path.DATASETS)
        ref_name = self.__config.get_value(constants.Sections.FILE, constants.File.REFERENCE)

        r_file = io.File(path_ds, ref_name)
        
        path_split_str =  self.__config.get_value(constants.Sections.PATH, constants.Path.DS_SPLIT)

        s_path = io.Path(os.path.join(path_split_str, r_file.get_name()))

        s_path.ensure_exists()
        s_path.delete_contents()

        max_gap = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.MAX_GAP))
        pair_length = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.READ_SIDE_LENGTH)) * 2
        max_content_length = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.SPLIT_REF_PAGING))

        c_corrector = max_content_length % (pair_length + max_gap)

        max_content_length = max_content_length - c_corrector

        f_content_temp = '' 
        i_file = 0

        is_first = True

        to_remove = ['\n', '\t', '\r', ' ']
        
        for is_last, line in r_file.read_iterator(to_remove):
            if (is_first):
                is_first = False
            else:
                f_content_temp += line

            if (len(f_content_temp) >= max_content_length or is_last):
                
                f_content = f_content_temp if is_last else f_content_temp[:max_content_length]

                self.__save_split(s_path, f_content, '%s' % i_file)

                i_file += 1

                f_content_temp = f_content_temp[max_content_length:]

    def __save_split(self, s_path, f_content, f_name):
        s_file = io.File(s_path.get_dir_path(), '%s.txt' % f_name)
        s_file.add('sequence', f_content)
        s_file.add('length', len(f_content))
        s_file.save()

    ##############################################################
    #KMER REF_FILE
    ##############################################################

    def kmerizer(self, kmer_length, kmer_gap):
        path_ds = self.__config.get_value(constants.Sections.PATH, constants.Path.DATASETS)
        ref_name = self.__config.get_value(constants.Sections.FILE, constants.File.REFERENCE)

        r_file = io.File(path_ds, ref_name)

        path_split_str =  self.__config.get_value(constants.Sections.PATH, constants.Path.KMER_INDEX)

        s_path = io.Path(os.path.join(path_split_str, r_file.get_name()))

        s_path.ensure_exists()

        s_path.create_sub('%s-%s' % (kmer_length, kmer_gap))

        s_path = s_path.get_sub_dir_obj('%s-%s' % (kmer_length, kmer_gap))

        s_path.ensure_exists()
        s_path.delete_contents()

        ref = genome.Reference(self.__config)

        kmer_col = collection.KmerList(kmer_length)
        r_kmer = ['']*(4**kmer_length)

        i = 0
        for i in xrange(0, ref.length() - kmer_length, kmer_gap):
            s = ref.read(i, i+kmer_length).get()
            j = kmer_col.index(s)
            r_kmer[j] += '%s,' % i

            if (i % 100000 == 0):
                self.__save_kmers(s_path, r_kmer, i)
                r_kmer = ['']*(4**kmer_length)

        self.__save_kmers(s_path, r_kmer, i)

        
    def __save_kmers(self, s_path, r_kmer, f_name):

        l_kmer = len(r_kmer)
        kmer_paging = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.KMER_VECT_PAGING))
        kmer_loop_length = int(math.ceil(l_kmer / float(kmer_paging)))

        s_file = io.File(s_path.get_dir_path(), '%s.txt' % f_name)

        if (s_file.exists()):
            s_file.load_as_fasta(['\n'])

        for i in xrange(kmer_loop_length):

            for j in xrange(i*kmer_paging, min(i*kmer_paging + kmer_paging, l_kmer)):
                if (r_kmer[j] != ''):
                    s_file.add(str(j), r_kmer[j])

        
        s_file.save()


        return r_kmer
                


class ReadFile:
    def __init__(self, config):
        self.__config = config

    def split(self):
        path_ds = self.__config.get_value(constants.Sections.PATH, constants.Path.DATASETS)
        reads_name = self.__config.get_value(constants.Sections.FILE, constants.File.READS)

        r_file = io.File(path_ds, reads_name)

        path_split_str =  self.__config.get_value(constants.Sections.PATH, constants.Path.DS_SPLIT)

        s_path = io.Path(os.path.join(path_split_str, r_file.get_name()))

        s_path.ensure_exists()
        s_path.delete_contents()

        max_number_lines = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.SPLIT_READ_LINES))

        is_first = True
        to_remove = ['\n', '\t', '\r', ' ']
        
        i_file = 0
        f_content = []

        for is_last, line in r_file.read_iterator(to_remove):
            if (is_first):
                is_first = False
            else:
                if (line != ''):
                    f_content.append(line)

            if (len(f_content) == max_number_lines or is_last):
                self.__save_split(s_path, f_content, '%s' % i_file)

                f_content = []
                i_file += 1

    def __save_split(self, s_path, f_content, f_name):
        s_file = io.File(s_path.get_dir_path(), '%s.txt' % f_name)
        s_file.add('lines', len(f_content))
        s_file.add('sequence', '\n'.join(f_content))
        s_file.save()

    ##############################################################
    #KMER READ_FILE
    ##############################################################
    def kmerizer(self, kmer_length):
        path_ds = self.__config.get_value(constants.Sections.PATH, constants.Path.DATASETS)
        reads_name = self.__config.get_value(constants.Sections.FILE, constants.File.READS)

        r_file = io.File(path_ds, reads_name)

        path_split_str =  self.__config.get_value(constants.Sections.PATH, constants.Path.KMER_INDEX)

        s_path = io.Path(os.path.join(path_split_str, r_file.get_name()))

        s_path.ensure_exists()

        s_path.create_sub('%s' % (kmer_length))

        s_path = s_path.get_sub_dir_obj('%s' % (kmer_length))

        s_path.ensure_exists()
        s_path.delete_contents()

        max_number_lines = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.SPLIT_READ_LINES))

        rl = collection.ReadList(self.__config)

        start = 0
        i = 0
        while (start <= rl.number_lines()):
            end = min(start + max_number_lines, rl.number_lines())
            read_list = rl.get_reads(start, end)
            
            f = io.File(s_path.get_dir_path(), '%s.txt' % i)

            if (f.exists()):
                f.load_as_fasta(['\n', ' ', '\r', '\t'])

            for j in xrange(len(read_list)):
                f.add(str(j), read_list[j].get_pair()[0].get_kmers(kmer_length, constants.Pair_Direction.STRAIGHTFORWARD))
                f.add(str(j), read_list[j].get_pair()[0].get_kmers(kmer_length, constants.Pair_Direction.REVERSE))
                f.add(str(j), read_list[j].get_pair()[1].get_kmers(kmer_length, constants.Pair_Direction.STRAIGHTFORWARD))
                f.add(str(j), read_list[j].get_pair()[1].get_kmers(kmer_length, constants.Pair_Direction.REVERSE))

            start = end + 1
            i += 1

            f.save()