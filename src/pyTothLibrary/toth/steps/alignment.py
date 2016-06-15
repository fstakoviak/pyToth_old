from toth.core import application, genome, collection, constants, io
from toth.steps import prepare
from random import randrange
import itertools

class Util:
    def __init__(self):
        pass

    def edit_distance(seq1, seq2):
        oneago = None
        rowsCols = []
        thisrow = range(1, len(seq2) + 1) + [0]
        for x in xrange(len(seq1)):
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
            for y in xrange(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)
            rowsCols.append(thisrow)
        return thisrow[len(seq2) - 1], rowsCols

    def construct_edit_distance(vector, s, t):
        aReversePath = ''
        bReversePath = ''

        i = len(s) - 1
        j = len(t) - 1

        while (i >= 0 and j >= 0):
            go_left = False
            go_up = False
            go_up_left = False

            if (j > 0):
                go_left = vector[i][j - 1] == vector[i][j] - 1
            else:
                go_left = False
                	
            if (i > 0):
                go_up = vector[i - 1][j] == vector[i][j] - 1
            else:
                go_up = False

            go_up_left = (not (go_left or go_up)) or (s[i] == t[j])

            if (go_up_left):
                aReversePath += s[i]
                bReversePath += t[j]
                i += -1
                j += -1
            #left
            elif (go_left):
                aReversePath += '-'
                bReversePath += t[j]
                j += -1
                keep_going = False				
            #upper
            elif (go_up):
                aReversePath += s[i]
                bReversePath += '-'
                i += -1
                keep_going = False

            return aReversePath[::-1], bReversePath[::-1]

class PreAlignment:
    def __init__(self, config):
        self.__config = config
        self.__kmer_pos_dict_t = dict()    
        self.__ref = genome.Reference(self.__config)


    def __random_split(self, s, length, count):
        random_v = []

        for i in xrange(count):
            n = randrange(0, len(s) - length)
            random_v.append(s[n : n + length])

        return random_v

    def __random_compare(self, seq, kmer_length, kmer_gap, max_pos_diff, n_split, side, direction):

        positions_dict = dict()
        pos_candidate_vect = []

        i = 0
        for rd in __random_split(seq, kmer_length, n_split):
            i_kmer = kmer_obj.index(rd)

            #list of sequences with kmer
            if (not self.__kmer_pos_dict_t.has_key(rd)):
                self.__kmer_pos_dict_t[rd] = self.__ref.get_kmer_positions(i_kmer, kmer_length, kmer_gap)

            kmer_pos_list = self.__kmer_pos_dict_t[rd]

            if (len(kmer_pos_list) > 0):
                positions_dict[i] = kmer_pos_list
                i += 1

        prod = []
        for i in xrange(len(positions_dict)):
            for j in xrange(i + 1, len(positions_dict)):
                prod.append([i , j])

        for x in xrange(len(prod)):

            vect_a = positions_dict[prod[x][0]]
            vect_b = positions_dict[prod[x][1]]

            for p in itertools.product(vect_a, vect_b):
                if (abs(p[0] - p[1]) <= max_pos_diff): 
                    pos_candidate_vect.append(p)

        return side, direction, pos_candidate_vect

    def __compare_repetition(self, seq, n_repetitions, kmer_config, max_diff, side, direction):

        for k_item in kmer_config:
            #print k_item
            for i in range(n_repetitions):
                t1 = self.__random_compare(seq, k_item[0], k_item[1], max_diff, k_item[2], side, direction)

                if (len(t1[2]) > 0):
                    return k_item, t1

        return None

    def run(self, start, end):
        c = self.__config

        kmer_obj = collection.KmerList(10)

        ref = genome.Reference(c)

        r_list = collection.ReadList(c)

        list_obj = r_list.get_reads(start, end)

        from toth.core import benchmark
        t = benchmark.Timer()

        i = 0

        line_aligned_dict = dict()

        for x in list_obj:

            print '[%s]' % i
            line_aligned_dict[i] = []

            left_seq = x.get_pair()[0].get()
            left_seq_rev = x.get_pair()[0].get(constants.Pair_Direction.REVERSE)
    
            right_seq = x.get_pair()[1].get()
            right_seq_rev = x.get_pair()[1].get(constants.Pair_Direction.REVERSE)

            k_config = [[10, 2, 10], [4, 2, 8]]
    
            t1 = self.__compare_repetition(left_seq, 2, k_config, 46, constants.Pair_Side.LEFT, constants.Pair_Direction.STRAIGHTFORWARD)
            t2 = self.__compare_repetition(left_seq_rev, 2, k_config, 46, constants.Pair_Side.LEFT, constants.Pair_Direction.REVERSE)

            t3 = self.__compare_repetition(right_seq, 3, k_config, 46, constants.Pair_Side.RIGHT, constants.Pair_Direction.STRAIGHTFORWARD)
            t4 = self.__compare_repetition(right_seq_rev, 3, k_config, 46, constants.Pair_Side.RIGHT, constants.Pair_Direction.REVERSE)

            is_unpaired = False

            t_left = None
            t_left_rev = None
            if (t1 == None and t2 == None):
                is_unpaired = True
            else:
                if (t1 != None):
                    t_left = set([x[0] for x in t1[1][2]]).union(set([x[1] for x in t1[1][2]]))
                if (t2 != None):
                    pass
                    t_left_rev = set([x[0] for x in t2[1][2]]).union(set([x[1] for x in t2[1][2]]))

            t_right = None
            t_right_rev = None
            if (t3 == None and t4 == None):
                is_unpaired = True
            else:
                if (t3 != None):
                    t_right = set([x[0] for x in t3[1][2]]).union(set([x[1] for x in t3[1][2]]))
                    pass
                if (t4 != None):
                    t_right_rev = set([x[0] for x in t4[1][2]]).union(set([x[1] for x in t4[1][2]]))
                    pass

            line_aligned_dict[i].append(t_left)
            line_aligned_dict[i].append(t_left_rev)
            line_aligned_dict[i].append(t_right)
            line_aligned_dict[i].append(t_right_rev)

            i += 1

            return line_aligned_dict


