import math
from toth.core import constants
from toth.core import io
from toth.core import collection
import os

class Alphabet:
    def __init__(self):
        pass

    def get_alphabet(self):
        return ['A', 'C', 'G', 'T']

    def dna_number_dict(self):
        d = dict()
        d['A'] = 1
        d['C'] = 2
        d['G'] = 4
        d['T'] = 8

        return d

class Sequence:
    """Class that represent a DNA sequence"""

    def __init__(self, seq):
        """Create an instance of a given sequence
        Attributes:
            seq (str): a DNA sequence
        """

        self.__alphabet = Alphabet().dna_number_dict()
        self.__seq = seq
        self.__seq_reverse = seq[::-1]
        self.__length = len(seq)
        self.__kmers = dict()
        self.__kmers_reverse = dict()

    def get(self, orientation = constants.Pair_Direction.STRAIGHTFORWARD):
        """Get the sequence string value
        Attributes:
            orientation (constants.Pair_Direction): the orientation of the sequence
        Returns:
            str: the sequence
        """

        if (orientation == constants.Pair_Direction.STRAIGHTFORWARD):
            return self.__seq
        elif(orientation == constants.Pair_Direction.REVERSE):
            return self.__seq_reverse

        return self.__seq

    def length(self):
        """Get the length of the sequence
        Returns:
            long: the length of the sequence
        """

        return self.__length

    def get_kmers(self, kmer_length, orientation = constants.Pair_Direction.STRAIGHTFORWARD):
        """Get the kmers of the sequence
        Attributes:
            kmer_length (int): the length of the kmer
            orientation (constants.Pair_Direction): the orientation of the sequence
        Returns:
            str: the corresponding kmers separated by ','
        """

        kl = collection.KmerList(kmer_length)

        kmer_dict = None
        seq_temp = None

        if (orientation == constants.Pair_Direction.STRAIGHTFORWARD):
            kmer_dict = self.__kmers
            seq_temp = self.__seq
        else:
            kmer_dict = self.__kmers_reverse
            seq_temp = self.__seq_reverse

        if (not kmer_dict.has_key(kmer_length)):
            kmer_dict[kmer_length] = ''

            for i in xrange(self.__length - kmer_length):
                kmer_dict[kmer_length] += str(kl.index(seq_temp[i : i + kmer_length])) + ','

        kmer_dict[kmer_length] = kmer_dict[kmer_length].rstrip(',')

        return kmer_dict[kmer_length]



class Reference:
    """Class to represent the Reference genome"""

    def __init__(self, config):
        """Create an instance of the Reference genome
        Attributes:
            config (toth.application.Config): config object
        """

        self.__config = config
        self.__length = None
        self.__kmer_positions_cache = dict()

    def read(self, start, end):
        """Get the reference sequence for the given interval
        Attributes:
            start (long): the start index
            end (long): the end index
        Returns
            toth.core.genome.Sequence: the sequence object
        """

        path_ds = self.__config.get_value(constants.Sections.PATH, constants.Path.DATASETS)
        ref_name = self.__config.get_value(constants.Sections.FILE, constants.File.REFERENCE)

        r_file = io.File(path_ds, ref_name)
        
        path_split_str =  self.__config.get_value(constants.Sections.PATH, constants.Path.DS_SPLIT)

        s_path = io.Path(os.path.join(path_split_str, r_file.get_name()))

        max_gap = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.MAX_GAP))
        pair_length = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.READ_SIDE_LENGTH)) * 2
        max_content_length = int(self.__config.get_value(constants.Sections.GENOME, constants.Genome.SPLIT_REF_PAGING))

        c_corrector = max_content_length % (pair_length + max_gap)

        max_content_length = max_content_length - c_corrector
        
        
        n_files = int(math.floor(end / max_content_length) - math.floor(start / max_content_length)) + 1

        to_remove = ['\n', '\t', '\r', ' ']

        s = ''
        for i in xrange(n_files):
            i_file = int(math.floor(start / max_content_length)) + i

            f = io.File(s_path.get_dir_path(), '%s.txt' % i_file)

            f.load_as_fasta(to_remove)
            s_current = f.get('sequence')

            i_start = start % max_content_length if i == 0 else 0
            i_end = end - (max_content_length * i_file)

            s += s_current[0][i_start : i_end]

        return Sequence(s)

    def length(self):
        """Get the length of the whole reference
        Returns
            long: the length of the reference
        """

        if (self.__length == None):
            self.__length = 0

            path_ds = self.__config.get_value(constants.Sections.PATH, constants.Path.DATASETS)
            ref_name = self.__config.get_value(constants.Sections.FILE, constants.File.REFERENCE)

            r_file = io.File(path_ds, ref_name)
        
            to_remove = ['\n', '\t', '\r', ' ']

            for _, l in r_file.read_iterator(to_remove):
                if (not l.startswith('>') and l != ''):
                    self.__length += len(l)

        return self.__length

    def get_kmer_positions(self, i_kmer, kmer_length, kmer_gap):
        """Get all positions on a Reference of a kmer
        Attributes:
            i_kmer (long): the numeric index representation of the kmer
            kmer_length (int): the length of the kmer
            kmer_gap (int): the interval between kmers
        Returns
            array: all positions of the kmer inside the Reference sequence
        """


        path_kmer = self.__config.get_value(constants.Sections.PATH, constants.Path.KMER_INDEX)
        ref_name = self.__config.get_value(constants.Sections.FILE, constants.File.REFERENCE)

        r_file = io.File('', ref_name)

        pos_vect = []

        path_obj = io.Path(os.path.join(path_kmer, r_file.get_name(), '%s-%s' % (kmer_length, kmer_gap)))

        for f in path_obj.get_files():
            f_obj = io.File(path_obj.get_dir_path(), f)
            f_obj.load_as_fasta(['\n', '\r', ' '])

            
            if (f_obj.has_key(i_kmer)):
                for i_str in f_obj.get(i_kmer)[0].strip(',').split(','):
                    if (i_str != ''):
                        i = int(i_str)
                        pos_vect.append(i)

        return pos_vect


class Read:
    """Class that represent a Paired read"""

    def __init__(self, id, left, right):
        """Create an instance of a paired read
        Attributes:
            id (int): id for the read
            left (str): left side of the read
            right (str): right side of the read
        """

        self.__id = id
        self.__left_seq = Sequence(left)
        self.__right_seq = Sequence(right)
    
    def get_pair(self):
        """Get all positions on a Reference of a kmer
        Returns
            tuple: the left and right sequence
        """

        return self.__left_seq, self.__right_seq

