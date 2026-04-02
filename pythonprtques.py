#take input from user find how many vowels are there
"""
word=input("Enter your word :")
count=0
if not word.isalpha():
    print("Enter a valid word")

vowel=["a","e","i","o","u"]

for letter in word:  #read each letter
    if letter in vowel:  #reads if that letter in vowel
     count+=1
print(count)



#count even and odd  
numbers=[1,4,6,7,5,3,8,9,6,66,4,3,4,2,5,4,6]
unique_numbers=set(numbers)
print(unique_numbers)
count1=0
count2=0

for num in unique_numbers:
    if num%2==0:
       count1 += 1         
print(count1,"are even")

for num in unique_numbers:
    if num%2!=0:
        count2 += 1
print(count2,"are odd")
"""
#reverse a list without using reverse()
lst = [1, 3, 4, 5]
new_list = []

for item in lst:
    new_list.insert(0, item)  # insert each element at index 0

print(new_list)


#print common elements of list 
list1=[1,3,4,5,6,7]
list2=[3,6,7,4]

for item1 in list1:
    for item2 in list2:
        if item1 == item2:
            print(item1 , end=" ")
             

#shopping list 

list=[]
"""
while True:
    prod=input("Enter your item =" )

    if prod== "done":
        print(list)
        break
           
    else :
          list.append(prod)
"""

#print largest numer 
numbers = [10, 5, 30, 25, 8]
numbers.sort(reverse=True)
print( "the largest number is " , numbers[0])


numbers = [10, 5, 30, 25, 8]
numbers.sort()
list=[]
for num in numbers:
    list.insert(0,num)
    
    
print("the largest number is",list[0])

"""
#PALINDROME 
# s1=input("enter your word :")
list=[]
for i in range(len(s1)):
     list.append(s1[i])
reversed_list= list[::-1] # new thing i learned as only reversing the string with reverse()wont store it

if list==reversed_list:
    print("Its a PALINDROME")

else:
    print("Its not a PALINDROME")
"""

"""
#find the missing number
numbers = [1,2,3,4,6,7,8]

for i in range(len(numbers)-1):
    if numbers[i+1]!= numbers[i] + 1:
          print(numbers[i]+1)
             
#to check if a number is prime (NICE QUESTION)
num=int(input("enter your number : "))

for i in range(2,num):

 if num%i==0 and num!= 2:
        print("number is not prime")
        break
else:
        print("number is prime")

"""
#find the frequency



"""
list=[1,2,2,3,4,4,5,6,6,7,7,7,8,9,9]

for num in set(list):
     print(num, "appears", list.count(num), "times")

"""
     #TUPLES


#recursion
#sum of n natural numbers 

def nsum(n):
    if n == 0:   # base case
        return 0
    return n + nsum(n-1)

print(nsum(4))


#recursion 
"""
def sum_list(lst):
    if not lst:
        return 0
    return lst[0] + sum_list(lst[1:])

lst=[3,4,5,6]
print(sum_list(lst))
#reverse  a string
def reverse(s):
    if len(s) == 1:
        return s
    return reverse(s[1:]) + s[0]

print(reverse("need"))
"""

"""
:
🟢 Easy

Write a function that takes a list of numbers and returns the sum of even numbers only.
Write a recursive function to find the power of a number — power(2, 5) → 32.
Write a lambda to filter out negative numbers from a list using filter().

🟡 Medium

Write a function using *args that returns the second largest number from the inputs.
Write a recursive function to count the number of digits in a number.
Write a function that takes another function as an argument and applies it twice — apply_twice(lambda x: x+3, 7) → 13.

🔴 Hard

Write a recursive function to flatten a nested list — [1, [2, [3, 4]], 5] → [1, 2, 3, 4, 5].
Write a recursive function to generate all permutations of a string.
Implement a memoized recursive solution for the coin change problem — find the minimum number of coins to make a target amount.

"""


        
def sum_even(lst):
    evenl = []
    for num in lst:
        if num % 2 == 0:
            evenl.append(num)
    return evenl          # ✅ outside the loop


def sum_list(lst):
    if not lst:
        return 0
    return lst[0] + sum_list(lst[1:])   # ✅ outside the if block


lst = [1, 3, 4, 5, 6]

even_numbers = sum_even(lst)
print(even_numbers)              # [4, 6]
print(sum_list(even_numbers))    # 10



