# what is a tuple? 1 
t = (1,2,3,4,5,62)
print(type(t))
# single element tuple 2
t1 = (1, )
print(type(t1))
# tuple without parenteses 3
t2 = 1,2,3
print(type(t2))
# empty tuple 4
t3 = ()
print(type(t3))
# tuples are immutable 5
try:
  t[0] = 3 
except:
  print("tuples are immutable")
# tuple lenght 6
print(len(t))
 # iterating over a tuple 
for i in t:
  print(i+1)
# 8 using index
for i in range(0, len(t)):
  print(t[i])
# tuple unpacking
t4 = (1,2,3)
a,b,c = t4
print(a, b, c)
#10 tuple extended unpacking
t4 = (1,2,33,4,5)
a,*b,c = t4
print(a,b,c)
# the two tuple methods
print("count", t4.count(33))
print("index", t4.index(33))
# 12 membership testing
if 33 in t4:
  print("yes")
# concat
print(t1 + t4)
#14 tuple repeat
print(t1 * 44)
# nested 
t5 = ((1,2),(2,3))
print(t5)
# 16 tuple to list 
print(type(t5))
print(type(list(t5)))
# soritng in reverse order 
print(t5)
print(t5[::-1])
# 18 sorting 
print(t4)
print(sorted(t4))
# tuple comprehension 
print(t4)
x= tuple(i for i in t4 if i%2==0)
print(x)
# 20 even umbers from tuple
t6 = (1,2,3,4,5,6,7,8,9,10)
t6_even = tuple(i for i in t6 if i%2 == 0)