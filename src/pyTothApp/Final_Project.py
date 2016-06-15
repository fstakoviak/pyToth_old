import datetime
from math import floor
import string
from cStringIO import StringIO
import sys
import random
from shutil import copyfile
import os, os.path

t0 = datetime.datetime.now()
print_array = []

#################################################

def get_time_diff(t, str):
    s = '== %s == %s' % ((datetime.datetime.now() - t), str)
    print_array.append(s)
    return s

#################################################

def clear_trackback():
    sys.exc_clear()
    sys.exc_traceback = sys.last_traceback = None

#################################################

def read_fasta(filePath):
    fileContent = {}
    for line in open(filePath, 'rU'):
        line = line.strip(' ').strip('\n').strip('\r')
        if line.startswith('>'):
            currentItem = line.strip('>')
            fileContent[currentItem] = []
        else:
            fileContent[currentItem].append(line)
    return fileContent

#################################################

def edit_distance(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]

#################################################

def edit_distance_iterator(ref_sub, side_pair, min_value):
    ref_sub_length = len(ref_sub)
    side_pair_length = len(side_pair)
    side_pair_reverse = side_pair[::-1]

    for i in xrange(ref_sub_length - side_pair_length + 1):

        current_ref_sub = ref_sub[i : i + side_pair_length]

        distance = edit_distance(current_ref_sub, side_pair)
        yield i, 1, distance
        
        if (distance <= min_value):        
            yield i, -1, edit_distance(current_ref_sub, side_pair_reverse)

#################################################

def edit_dict_min_values(dict_value, index_edit, min_value):

    return_vect = []
    for v in dict_value:
        if (min_value > v[index_edit]):
            min_value = v[index_edit]
            return_vect = []

        if (min_value == v[index_edit]):
            return_vect.append(v)

    return return_vect, len(return_vect), min_value

#################################################

def edit_pair_distance(ref_sub, left_pair, right_pair, min_gap, max_gap, min_value, right_overlap, is_first, start_index):
    
    gap_length = max_gap - min_gap
    final_result_edit = []
    final_result_length = 0

    #LEFT PAIR

    left_pair_sub = ref_sub[0 : len(ref_sub) - len(right_pair) - max_gap]
    left_pair_edit = []
    
    last_i = 0
    q_left_pair = len(left_pair_sub) - len(left_pair)
  
    for i, direction, distance in edit_distance_iterator(left_pair_sub, left_pair, min_value):
        i = i + start_index

        if (distance <= min_value):
            left_pair_edit.append([i, direction, distance])

    if (len(left_pair_edit) > 0):

        #RIGHT PAIR

        right_start_index = len(left_pair) + min_gap + (0 if is_first else gap_length - 1)

        right_pair_sub = ref_sub[right_start_index:]
        right_pair_edit = []

        for j, direction, distance in edit_distance_iterator(right_pair_sub, right_pair, min_value):
            j = j + start_index + right_start_index
            if (distance <= min_value):
                right_pair_edit.append([j, direction, distance])

        right_pair_edit.extend(right_overlap)

        right_overlap = []

        if (len(left_pair_edit) > 0):
            for left_row in left_pair_edit:
                min_right_index = left_row[0] + len(left_pair) + min_gap
                max_right_index = left_row[0] + len(left_pair) + max_gap
                temp_vect = (right_row for right_row in right_pair_edit if (right_row[0] >= min_right_index and right_row[0] <= max_right_index))
                for right_row in temp_vect:
                    sum_temp = left_row[2] + right_row[2]
                    if (sum_temp < min_value):
                        min_value = sum_temp
                        final_result_edit = []
                    if (sum_temp == min_value):
                        final_result_edit.append([left_row[0], left_row[1], left_row[2], right_row[0], right_row[1], right_row[2], sum_temp])


        final_result_edit, final_result_length, min_value = edit_dict_min_values(final_result_edit, 6, min_value)

        for right_row in right_pair_edit:
            if (right_row[0] > len(right_pair_sub) - len(right_pair) - gap_length + 1) and (right_row[2] <= min_value):
                right_overlap.append(right_row)

    return final_result_edit, final_result_length, min_value, right_overlap

#################################################

def paging_ref_sub_iterator(ref, q_left_pair, paging_length):
    i = len(ref)
    while (i > 0):
        yield ref[0:paging_length]
        ref = ref[q_left_pair:]
        ref_length = len(ref)
        i = i - q_left_pair

#################################################

def min_ref_sub_read(ref_sub, left_pair, right_pair, min_gap, max_gap, min_value, sub_read_length, number_of_sub_reads, min_matches):

    if (min_value == 0):
        return False
    
    ref_sub_length = len(ref_sub)
    left_pair_length = len(left_pair)
    right_pair_length = len(right_pair)

    #sub_read_length = 3

    #number_of_sub_reads = sub_read_length^3
    #min_matches = number_of_sub_reads * 0.95

    pair_random_read = []


    for i in xrange(number_of_sub_reads):     
           
        max_random_left = left_pair_length - sub_read_length
        random_offset_left = random.randint(0, max_random_left)
        sub_left =left_pair[random_offset_left : random_offset_left + sub_read_length]

        max_random_right = right_pair_length - sub_read_length
        random_offset_right = random.randint(0, max_random_left)
        sub_right = right_pair[random_offset_right : random_offset_right + sub_read_length]

        pair_random_read.append([sub_left, sub_right])

    current_n_matches = 0
    for i in xrange(number_of_sub_reads):

        left_sub_string = pair_random_read[i][0]
        right_sub_string = pair_random_read[i][1]

        left_find_index_min = 0
        left_find_index_max = ref_sub_length - right_pair_length - min_gap

        for l_sub in [left_sub_string, left_sub_string[::-1]]:
            left_find_index = ref_sub.find(l_sub, left_find_index_min, left_find_index_max)

            if (left_find_index != -1):
                right_find_index_min = ((left_find_index - left_pair_length) if (left_find_index > left_pair_length) else 0) + left_pair_length + min_gap
                right_find_index_max = right_find_index_min + (max_gap - min_gap) + right_pair_length + left_pair_length

                if (ref_sub.find(right_sub_string, right_find_index_min, right_find_index_max) != -1):
                    current_n_matches += 1

                if (ref_sub.find(right_sub_string[::-1], right_find_index_min, right_find_index_max) != -1):
                    current_n_matches += 1

    return (current_n_matches >= min_matches)

#################################################

def ref_read_edit_paging(ref, left_pair, right_pair, min_gap, max_gap, paging_length):

    final_result_edit = []
    final_result_edit_length = 0
    min_value = len(ref)
    q_left_pair = paging_length - len(right_pair) - max_gap - len(left_pair)
    ref_lenght = len(ref)

    print get_time_diff(t0, 'BEGIN PAGING = %s' % paging_length)
    
    right_overlap = []
    is_first = True

    start_index = 0

    for ref_sub in paging_ref_sub_iterator(ref, q_left_pair, paging_length):
        


        if (min_ref_sub_read(ref_sub, left_pair, right_pair, min_gap, max_gap, min_value, 16, 20, 2)):
        #if (True):

            final_result_temp, final_result_length_temp, min_value_temp, right_overlap = edit_pair_distance(ref_sub, left_pair, right_pair, min_gap, max_gap, min_value, right_overlap, is_first, start_index)


            if (final_result_length_temp > 0):
            
                if (min_value > min_value_temp):
                    min_value = min_value_temp
                    final_result_edit = []
                    final_result_edit_length = 0

                final_result_edit.extend(final_result_temp) 
                final_result_edit_length = final_result_edit_length + final_result_length_temp

        print get_time_diff(t0, 'PARTIAL [%s]: min_value[%s], result_count[%s]' % (paging_length, min_value, final_result_edit_length))

        is_first = False
        start_index = start_index + q_left_pair
            
    print get_time_diff(t0, 'END PAGING = %s' % paging_length)


    return final_result_edit

#################################################

#copyfile('./Final_Project.py', '../../Backup/Final_Project_%s.py' % len(os.listdir('../../Backup/')))

directory_path = os.path.dirname(os.path.abspath(__file__))
#print os.getcwd()

ref = ''.join(read_fasta('%s/datasets/ref_hw1_W_2_chr_1.txt' % directory_path).values()[0])
reads = read_fasta('%s/datasets/reads_hw1_W_2_chr_1.txt' % directory_path)



min_gap = 81
max_gap = 131

print get_time_diff(t0, 'BEGIN')

ref_length = len(ref)
z = 0

start_line = 0
end_line = 2999

if (len(sys.argv) > 2):
    end_line = int(sys.argv[2])
if (len(sys.argv) > 1):
    start_line = int(sys.argv[1])

for read_pair in reads.values()[0]:
    
    if (z >= start_line and z <= end_line):
        
        print get_time_diff(t0, 'LINE [%s]' % z)
    
        left_part_min = ref_length

        pair_vect = [p.strip(' ').strip('\n').strip('\r') for p in read_pair.split(',')]
        left_pair = pair_vect[0]
        right_pair = pair_vect[1]
        pair_length = len(left_pair)

        paging_size = 600

        print get_time_diff(t0, 'PAGING SIZE BEFORE [%s]' % paging_size)

        p_corrector = paging_size % (len(left_pair) + len(right_pair) + max_gap)

        paging_size = paging_size - p_corrector

        print get_time_diff(t0, 'PAGING SIZE CORRECTED [%s]' % paging_size)


        final_result_edit = ref_read_edit_paging(ref, left_pair, right_pair, min_gap, max_gap, paging_size)

        final_result_string = []
        final_result_string.append('>>> RESULT')
        
        for x in final_result_edit:
            x_str = '['
            for y in x:
                x_str += '%s, ' % y

            x_str = x_str[:len(x_str) - 2] + ']'

            final_result_string.append(x_str)

        print_array.extend(final_result_string)
        
        if (len(final_result_edit) == 0):
            with open('%s/results/_%s.txt' % (directory_path, z), 'w') as file_:
                file_.write('\n'.join(print_array))
        else:
            with open('%s/results/%s.txt' % (directory_path, z), 'w') as file_:
                file_.write('\n'.join(print_array))

        print_array = []

    z = z + 1

print get_time_diff(t0, 'END')