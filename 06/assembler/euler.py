import sys

s = [i for i in 'abcdefghijklm']
a = []
n = 2
for i in range(13, 0, -1):
    idx, n = divmod(n, i)
    a.append(s.pop(idx))
print(''.join(a))