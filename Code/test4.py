my_list = [1, 2, 3, 4, 5]

# Iterate through the list in pairs
it = iter(my_list)

for first_element, second_element in zip(it, it):
    print(f"First Element: {first_element}, Second Element: {second_element}")
