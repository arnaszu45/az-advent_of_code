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


def print_test_case_matching_lines(path: Path, file_text: str, pattern: str):
    print(f'TestCase APPROACH\n{path} \n')
    for i, line in enumerate(file_text.splitlines()):
        if pattern in line:
            line = line.strip()
            if not line.startswith('def ') and not line.startswith('self.'):
                print(f'{i - 1}: {line}')


def print_not_test_case_matching_lines(path: Path, file_text: str, pattern: str):
    """Prints out if it's """

    print(f'\nNOT TestCase APPROACH\n{path} \n')
    for i, line in enumerate(file_text.splitlines()):
        if pattern in line:
            line = line.strip()
            print(f'{i - 1}: {line}')


def find_pattern_in_functions(directory: Path, pattern: str, n: int) -> list[str]:
    polarion_list = []
    function_list = []
    list_of_repeated_definition = []

    if n == 0:
        return polarion_list
    n = n - 1

    print(f"Searching for '{pattern}' in {directory}\n")
    single_files = list(directory.rglob("*.py"))

    for path in single_files:
        file_text = path.read_text(encoding="UTF-8")
        function_usages = find_all_pattern_usages(file_text, pattern)
        function_definition_usages = re.findall(fr'def {pattern}\b', file_text)
        list_of_repeated_definition.extend(function_definition_usages)

        if len(list_of_repeated_definition) > 1:
            print('ERROR: There is more than 1 usages of function definition \n')
            return polarion_list

        if pattern in file_text:
            if "/test_cases/" in path.as_posix() and path.match("test_*.py"):
                polarion_list.append(search_for_id_pattern(file_text, 'Polarion ID:'))
                print_test_case_matching_lines(path, file_text, pattern)
            else:
                for index in function_usages:
                    function_name = get_function_name(index, file_text)
                    if function_name != pattern:
                        function_list.append(function_name)
                        print_not_test_case_matching_lines(path, file_text, pattern)

    for function in set(function_list):
        polarion_list.extend(find_pattern_in_functions(directory, function, n))
    return polarion_list


def main(directory: Path, pattern: str, depth: int):
    list_of_ids = find_pattern_in_functions(directory, pattern, depth)
    print(list_of_ids)
    print(len(set(list_of_ids)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, required=True,
                        help="The pattern what should be looked for in files")
    parser.add_argument("-n", "--number_of_depth", type=int, required=True, default=5,
                        help="The depth or the number of recursive calls the function should make.")
    args = parser.parse_args()
    main(directory=args.test_automation_dir, pattern=args.pattern, depth=args.number_of_depth)