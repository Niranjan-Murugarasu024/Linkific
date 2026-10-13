numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

squares = [number ** 2 for number in numbers]
even_numbers = [number for number in numbers if number % 2 == 0]

prices = {
    "keyboard": 1200,
    "mouse": 600,
    "monitor": 12000,
}

discounted_prices = {
    item: price * 0.90
    for item, price in prices.items()
}

print("Squares:", squares)
print("Even numbers:", even_numbers)
print("Discounted prices:", discounted_prices)