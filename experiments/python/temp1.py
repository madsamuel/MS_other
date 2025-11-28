sum = [2,77,3,6]
target = 5

def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 0, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
            # else:
            #     return []
            
print(two_sum(sum, target))