dict_a = {}
dict_b = {}
tag = 0
for i in range(0,26):
    dict_a[chr(ord('a')+i)] = 0
    dict_b[chr(ord('a') + i)] = 0
aaa = input()
bbb = input()
for i in aaa:
    dict_a[i] += 1
for i in bbb:
    dict_b[i] +=1
for i in range(0,25):
    if dict_a[chr(ord('a') + i)] != dict_b[chr(ord('a') + i)]:
        print("false")
        tag = 1
        break
if tag == 0:
    print("true")


