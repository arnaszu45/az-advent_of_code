f = open("advent_of_code_1_input", 'r')
txt = f.read()
one_line = txt.splitlines()

def get_number(string):
    for i in string:
        if i.isdigit():
            first_value = i
            break
    reversed_string = string[::-1]
    for j in reversed_string:
        if j.isdigit():
            second_value = j
            break
    return first_value+second_value

sum_of_all_values = 0
for element in one_line:
    value = int(get_number(element))
    sum_of_all_values += value
    print(sum_of_all_values)