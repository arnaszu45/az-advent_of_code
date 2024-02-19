from pathlib import Path
p = Path("advent_of_code_1_input")
p = p.read_text()
lines = p.splitlines()

dictionary = {}
dictionary['one'] = '1'
dictionary['two'] = '2'
dictionary['three'] = '3'
dictionary['four'] = '4'
dictionary['five'] = '5'
dictionary['six'] = '6'
dictionary['seven'] = '7'
dictionary['eight'] = '8'
dictionary['nine'] = '9'

def converter(line, dictionary):
    char = 0
    while char < len(line):
        for word, number in dictionary.items():
            if line.startswith(word, char):
                line = line.replace(word, number)
        char += 1
    return line

def get_number(line):

    first_value = "0"
    for char in line:
        if char.isdigit():
            first_value = char
            break

    second_value = "0"
    for char in reversed(line):
        if char.isdigit():
            second_value = char
            break
    return first_value+second_value

def main():
    sum_of_all_values = 0
    for element in lines:
        converted_line = converter(element, dictionary)
        value = int(get_number(converted_line))
        sum_of_all_values += value
    print(sum_of_all_values)

main()