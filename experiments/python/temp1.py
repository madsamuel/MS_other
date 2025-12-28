s = "5"
print(int(s))
print(type(int(s)))
#1 convert a list to string
list = ["a","b"]
print(' '.join(list))
# 2 Convert a list to string using the map() function
list = ["Hellow","John","?",1,2,3]
mystring = ' '.join(map(str,list))
print(mystring)
# Hellow John ? 1 2 3
# 3
text= "the rain in spaine fails mainly on the rain"
print(text.find("rain"))
#4 
print(text.index("s"))
#5 
i = "2"
print(i.isnumeric())
#6
txt = "50"
x = txt.zfill(10)
print(x) # True
#7 List to string
ListL = ["a","b","v","c"]
print("".join(ListL))
#8 
if 'r' in text:
    print(True)
#9  Round to two decimals
dec = 123.456
print(round(dec, 2))
#10 format() function takes 
print(format(dec,".2f"))