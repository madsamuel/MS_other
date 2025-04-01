# You are given an array prices where prices[i] is the price of a given stock on the  day.

# You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

# Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.

# Examples
# Input: [3, 2, 6, 5, 0, 3]
# Expected Output: 4
# Justification: Buy the stock on day 2 (price = 2) and sell it on day 3 (price = 6). Profit = 6 - 2 = 4.
# Input: [8, 6, 5, 2, 1]
# Expected Output: 0
# Justification: Prices are continuously dropping, so no profit can be made.
# Input: [1, 2]
# Expected Output: 1
# Justification: Buy on day 1 (price = 1) and sell on day 2 (price = 2). Profit = 2 - 1 = 1.

prices = [3, 2, 6, 5, 0, 3]
min_price = float('inf')
max_profit = 0

for p in prices:
    if p < min_price:
        min_price = p
    elif p - min_price > max_profit:
        max_profit = p - min_price

print(max_profit)