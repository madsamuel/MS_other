# Input: [3, 2, 6, 5, 0, 3]
# Expected Output: 4
# Justification: Buy the stock on day 2 (price = 2) and sell it on day 3 (price = 6). Profit = 6 - 2 = 4.Input: [3, 2, 6, 5, 0, 3]
# Expected Output: 4
# Justification: Buy the stock on day 2 (price = 2) and sell it on day 3 (price = 6). Profit = 6 - 2 = 4.

Input = [3, 2, 6, 5, 0, 3]

def max_profit(prices):        
    if not prices:
        return 0

    min_price = prices[0]
    max_profit = 0

    for price in prices:
        if price < min_price:
            min_price = price
        else:
            profit = price - min_price
            max_profit = max(max_profit, profit)

    return max_profit

print(max_profit(Input))