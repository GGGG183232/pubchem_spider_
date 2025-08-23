print("input num:")
num = input()
list = []
dict = {}
print("input the list:")
for i in range(0, int(num)):
    aaa = input()
    list.append(int(aaa))
list = sorted(list)
for i in range(0, len(list)):
    for j in range(i+1, len(list)):
        dict[list[i]+list[j]] = [str(list[i]),str(list[j])]
print("input_the_sum:")
sum = input()
print(dict[int(sum)])

