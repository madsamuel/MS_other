## 🧠 Longest Consecutive Subsequence
## ##Difficulty**: Medium  
## **Tags**: Array, HashSet, Algorithms

### 📝 Problem Statement
# Given an unsorted array of integers `nums`, return the **length of the longest consecutive elements sequence**.
# You must write an algorithm that runs in **O(n)** time.
### 🔍 Example

# nums = [100, 4, 200, 1, 3, 2] -> 4 (The longest consecutive elements sequence is [1, 2, 3, 4]. Therefore its length is 4.)
# nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1] -> 9 (The longest consecutive elements sequence is [0, 1, 2, 3, 4, 5, 6, 7, 8]. Therefore its length is 9.)
# nums = [10, 5, 12, 3, 55, 11, 13] -> 4 (The longest consecutive elements sequence is [10, 11, 12, 13]. Therefore its length is 4.)

nums = [100, 4, 200, 1, 3, 2]
nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]
# convert nums to a ordered dircitionary    

seen = set() 
for num in nums:
    if num + 1 in nums:
        seen.add(num)
    if num - 1 in nums:
        seen.add(num)
    
# sort  by value    
sorted_items = sorted(seen)  
print(sorted_items)
