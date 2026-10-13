# List: ordered and mutable
columns = ["id", "name", "date"]
columns.append("amount")

# Tuple: ordered and immutable
database_config = ("localhost", 5432, "analytics")

# Set: unique values
source_systems = {"csv", "json", "csv", "api"}

# Dictionary: key-value pairs
record = {
    "id": 101,
    "name": "Customer A",
    "amount": 2500.50,
}

print(columns)
print(database_config)
print(source_systems)
print(record)

print("Customer:", record["name"])
print("Missing field:", record.get("email", "Not provided"))