from pathlib import Path
import re
data = (Path('aoc_d3_input').read_text())


def get_location_around(numbers_loc: int, numbers_length: int, line_length: int, lines: str):
    from_left = numbers_loc - 1
    from_right = numbers_loc + numbers_length
    under = lines[from_left-line_length:from_right-line_length]
    if from_left - line_length > 0:
        above = lines[from_left - line_length:from_right - line_length]
        print(above, lines[from_left], lines[from_right], under)
    else:
        print(lines[from_left], lines[from_right], under)




numbers = re.findall(r'\d+', data)
line_length = len(data.splitlines())
loc = 0
for number in numbers:
    numbers_length = len(number)
    loc = data.find(number, loc)
    get_location_around(loc, numbers_length, line_length, data)


