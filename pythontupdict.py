t=(1,2,3,4,5)
print(t[2])
print(len(t))
print(2 in t)
l=list(t)
print(l)


tuple=(1,4,3,6,5,8,7)
l1=list(tuple)
l1.sort()
print(l1[len(tuple)-1] , "is max")
print(l1[0], "is min")
#unpacking of tuple
tuple1=(10,20,30)

a,*b = tuple1

print(a)
print(b)

tup=(1,2,3)
a,b,c= tup
print(a)
print(b)
print(c)
"""
Create a dictionary with 3 students and their marks.

Print all keys of the dictionary.

Print all values of the dictionary.

Add a new key-value pair to a dictionary.

Update the marks of a student.
"""

dict3={"Rahul":90 ,"Somya":80, "Harish":78 }


print(dict3.keys())
print(dict3.values())
dict3["aish"]=60
dict3["Rahul"]= 78
print(dict3)

d1 = {'a':1,'b':2}
d2 = {'c':3,'d':4}
d3=d1|d2
print(d3)



d = {'Rahul':85,'Anu':92,'Riya':78}

sorted_dict = dict(sorted(d.items(), key=lambda x: x[1]))

print(sorted_dict)

#Write a program that stores names as keys and counts number of letters in the name as value.

names = ["Ram", "Shyam", "Anu"] #input list

d = {name: len(name) for name in names}

print(d)


dict={x:x**2 for x in range(5)}
print(dict)

#invert a dictionary
dict5 = { "a": 1 , "b": 2 , "c": 3}
inv = {}

for key in dict5:
    value = dict5[key]
    inv[value] = key

print(inv)

#count thefrequency using dictionary
list = [1,2,1,3,2,1]
for num in set(list):
 dict9 ={num:list.count(num)}
  
  
 print(dict9)