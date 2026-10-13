def convert_to_integer(value):
    try:
        return int(value)

    except ValueError:
        print(f"Invalid integer: {value!r}")
        return None

    finally:
        print("Conversion attempt finished")


print(convert_to_integer("125"))
print(convert_to_integer("abc"))