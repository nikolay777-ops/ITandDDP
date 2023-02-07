list_1 = [1, 2, 3]
list_2 = [1, 2, 4]

list_1.extend(list_2)

lox = {1, 2, 3, 5, 6}
lox_str = str(lox)

print(str(lox).replace('{','').replace('}', ''))