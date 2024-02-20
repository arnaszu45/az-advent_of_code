import re
from pathlib import Path
p = Path("advent_of_code_day_2_input")
p = p.read_text()
games = p.splitlines()

red = 12
green = 13
blue = 14

a = "Game 1: 1 blue, 8 green; 14 green, 15 blue; 3 green, 9 blue; 8 green, 8 blue, 1 red; 1 red, 9 green, 10 blue"
b = "Game 2: 3 blue, 1 green, 2 red; 2 red, 2 green, 5 blue; 3 green, 10 blue; 8 red, 1 blue; 3 red, 1 green, 5 blue; 1 blue, 5 red, 3 green"


def colour_counter(input_line : str, colour : str):
    count = '0'
    if colour in input_line:
        find_colour_place = input_line.find(colour)
        first_coordinate = find_colour_place - 3
        if first_coordinate < 0:
            first_coordinate = 0
        count = input_line[first_coordinate:find_colour_place]
    return int(count)


print(colour_counter(a, 'blue'))

def game_rules(single_game):
    if colour_counter(single_game, 'red') <= red:
        print(colour_counter(single_game, 'red'))
        if colour_counter(single_game, 'blue') <= blue:
            print(colour_counter(single_game, 'blue'))
            if colour_counter(single_game, 'green') <= green:
                print(colour_counter(single_game, 'green'))
                print("WON")
                return True
    else:
        print('NOT WON')
        return False


def main():
    game_number = 1
    sum_of_numbers_of_game = 0
    for game_inx in games:
        print(game_inx)
        game_inx = game_inx.split(';')
        for single_game in game_inx:
            print(single_game)
            if game_rules(single_game):
                sum_of_numbers_of_game += game_number
                print(sum_of_numbers_of_game)
                game_number = game_number + 1
                print(game_number)
                print(sum_of_numbers_of_game)
                break
    print(sum_of_numbers_of_game)


def main():
    game_number = 1
    sum_of_numbers_of_game = 0
    for game_inx in games:
        print(game_inx)
        game_inx = game_inx.split(';')
        # print(single_game)
        if game_rules(game_inx) == True:
            sum_of_numbers_of_game += game_number
            print(sum_of_numbers_of_game)
            game_number = game_number + 1
            print(game_number)
            print(sum_of_numbers_of_game)
    print(sum_of_numbers_of_game)


main()