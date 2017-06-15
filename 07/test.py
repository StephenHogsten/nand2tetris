import sys
import os

a = sys.argv[1]
# print(a)
# print(os.listdir(a))
b = open(a, 'r')
print(b.read())
b.close()
