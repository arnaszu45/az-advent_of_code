from pathlib import Path
import argparse
import re


def search_for_id_pattern(file_text: str, pattern: str) -> str:
    """Search for specific pattern and collects it into list of strings"""

    id_index = file_text.find(pattern)
    if id_index > 0:
        remaining_text = file_text[id_index + len(pattern):]
        remaining_text = remaining_text.split()[0]
        polarion_id = remaining_text.strip()
        print(f'\n{polarion_id}')
        return polarion_id
    else:
        polarion_id = ''
        return polarion_id


def get_function_name(start_pos: int, file_text: str) -> str:
    """Returns only function name used before specific pattern"""

    function_starts = file_text.rfind('def ', 0, start_pos) + len('def ')
    if function_starts > start_pos:
        return ''
    else:
        function_ends = file_text.find('(', function_starts)
        function_name = file_text[function_starts:function_ends]
        if '\n' in function_name:
            return ''
        return function_name


def find_all_pattern_usages(text: str, pattern: str) -> list[int]:
    """Returns a list of positions where pattern appears in string"""

    start = 0
    functions_indexes = []
    while start != -1:
        start = text.find(pattern, start)
        if start == -1:
            continue
        functions_indexes.append(start)
        start += len(pattern)
    return functions_indexes


def find_pattern_in_functions(directory: Path, pattern: str, polarion_list: list, n: int) -> list[str]:

    if n == 0:
        return polarion_list
    n = n - 1

    print(f"Searching for '{pattern}' in {directory}\n")
    single_files = list(directory.rglob("*.py"))
    function_list = []

    for path in single_files:
        file_text = path.read_text(encoding="UTF-8")
        function_usages = find_all_pattern_usages(file_text, pattern)
        amount_of_function = len(re.findall(fr'def {pattern}\b', file_text))

        if amount_of_function > 1:
            print('ERROR: There is more than 1 usages of function definition \n')
            return polarion_list

        if pattern in file_text:
            if "/test_cases/" in path.as_posix() and path.match("test_*.py"):
                if 'def ' + pattern or 'def test_' not in file_text:
                    polarion_list.append(search_for_id_pattern(file_text, 'Polarion ID:'))
                    print(f'TestCase APPROACH\n{path} \n')
                    for i, line in enumerate(file_text.splitlines()):
                        line = line.strip()
                        if pattern in line:
                            if not line.startswith('def test_') or not line.startswith('self'):
                                print(f'{i - 1}: {line}')
            else:
                for index in function_usages:
                    function_name = get_function_name(index, file_text)

                    if pattern in file_text:
                        if function_name != pattern:
                            print(f'\nNOT TestCase APPROACH \n{path} \n')
                            function_list.append(function_name)
                            for i, line in enumerate(file_text.splitlines()):
                                if pattern in line:
                                    print(f'{i - 1}: {line.strip()}')

    for function in set(function_list):
        find_pattern_in_functions(directory, function, polarion_list, n)

    #Keeping old version, in order to input new one without breaking it
# def find_pattern_in_functions(directory: Path, pattern: str, polarion_list: list, n: int):
#
#     if n == 0:
#         return polarion_list
#     n = n - 1
#
#     print(f"Searching for '{pattern}' in {directory} directory \n")
#     single_files = list(directory.rglob("*.py"))
#     functions_list = []
#
#     for path in single_files:
#         file_text = path.read_text(encoding="UTF-8")
#         for i, line in enumerate(file_text.splitlines()):
#             if pattern in line:
#                 line = line.strip()
#                 if "/test_cases/" in path.as_posix() and path.match("test_*.py"):
#
#                     if not line.startswith('def '):
#                         if '_' + pattern not in line:
#                             search_for_pattern(file_text, polarion_list, 'Polarion ID:')
#                             print(f'TestCase APPROACH \n{path} \n{i}:    {line}\n')
#
#                 elif not line.startswith('def '):
#                     print(f'NOT TestCase APPROACH \n{path} \n{line.strip()} \n')
#                     index_of_def = file_text.index(line)
#                     function_name = get_function_name(index_of_def, file_text)
#                     functions_list.append(function_name)
#


    # print(functions_list)
    # function = functions_list[0]
    # find_pattern_in_functions(directory, function, polarion_list, n)


def main(directory: Path, pattern: str):
    polarion_list = []
    find_pattern_in_functions(directory, pattern, polarion_list, 4)
    print(polarion_list)
    print(len(set(polarion_list)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, required=True,
                        help="The pattern what should be looked for in files")
    args = parser.parse_args()
    main(directory=args.test_automation_dir, pattern=args.pattern)