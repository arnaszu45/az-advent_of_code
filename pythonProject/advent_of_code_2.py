d = {}
d['one'] = '1'
d['two'] = '2'
d['three'] = '3'
d['four'] = '4'
d['five'] = '5'
d['six'] = '6'
d['seven'] = '7'
d['eight'] = '8'
d['nine'] = '9'

f = open("advent_of_code_1_input", 'r')
txt = f.read()
one_line = txt.splitlines()

a = "sixsrvldfour4seven"

def converter(string, dictionary):
    result = ''
    i = 0
    while i < len(string):
        found = False
        for word, number in dictionary.items():
            if string.startswith(word, i):
                print(i)

