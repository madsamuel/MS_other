nums = [3,3] 
target = 6

seen = []

for i in nums:
    if target - i in seen:
        print(seen.index(target-i), nums.index(i))
    else:
        seen.append(i)