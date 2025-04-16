
l1 = [2,4,3]
l2 = [5,6,4]

# l1 = [9,9,9,9,9,9,9]
l2 = [9,9,9,9]

sum = []
val = 0
x1 = 0
x2 = 0
carry = 0

while x1 < len(l1) and x2 < len(l2):
    val = l1[x1] + l2[x2] + carry
    if val >= 10:
        carry = 1
        val = val % 10
    else:
        carry = 0
    sum.append(val)
    x1 += 1
    x2 += 1

if x1 < len(l1):
    while x1 < len(l1):
        sum.append(l1[x1])
        x1 += 1
if x2 < len(l2):
    while x2 < len(l2):
        sum.append(l2[x2])
        x2 += 1
if carry > 0:
    sum.append(carry)


print(sum)