def calculate_total(values):
    return sum(values)


def calculate_average(values):
    if not values:
        return 0

    return sum(values) / len(values)


records = [100, 200, 300, 400]

print("Total:", calculate_total(records))
print("Average:", calculate_average(records))

# A small anonymous function
sort_by_length = lambda filename: len(filename)

filenames = ["a.csv", "customer_data.csv", "sales.json"]
print(sorted(filenames, key=sort_by_length))