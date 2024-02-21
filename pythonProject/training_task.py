from pathlib import Path
import os
list_of_files = []
for path, subdir, files in os.walk(Path('TestAutomation')):
    for name in files:
        file = os.path.join(path, name)
        list_of_files.append(file)


for file in list_of_files:
    with open(file, 'r') as single_file:
        if 'cleaning.start_cleaning' in single_file:
            print(single_file)