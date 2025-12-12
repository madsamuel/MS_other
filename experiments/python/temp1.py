nums = [3, 3]
target = 6

seen = []
for i in nums:
    if i in seen:
        print(True)
        # stop the app
        break
    else:
        seen.append(i)

print(False)

