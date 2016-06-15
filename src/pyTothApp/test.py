#a = []
import toth.core

#a.append([1, 5])
#a.append([2, 4])
#a.append([3, 3])
#a.append([6, 2])

#print max([x[0] for x in a])

#b = [5, 4, 2, 6, 2]

#print b.index(0)

a = toth.core.application.Util()

list_length = 10
number_of_splits = 3

print a.get_split_redundancy(list_length, number_of_splits, 0)
print a.get_split_redundancy(list_length, number_of_splits, 1)
print a.get_split_redundancy(list_length, number_of_splits, 2)

