from pathlib import Path
import argparse
import re
import time

processed_functions = set()


def search_for_id_pattern(file_text: str, pattern: str) -> str:
    """Search for specific pattern, prints and returns it as a string"""

    id_index = file_text.find(pattern)
    if id_index != -1:
        remaining_text = file_text[id_index + len(pattern):]
        remaining_text = remaining_text.split()[0]
        polarion_id = remaining_text.strip()
        print(f'\n{polarion_id}')
        return polarion_id
    else:
        return ''


def get_function_name(start_pos: int, file_text: str) -> str:
    """Returns only function name used before specific position"""

    function_starts = file_text.rfind('def ', 0, start_pos) + len('def ')
    if function_starts > start_pos:
        return ''
    else:
        function_ends = file_text.find('(', function_starts)
        function_name = file_text[function_starts:function_ends]
        if '\n' in function_name:
            return ''
        return function_name


def find_matching_lines(file_text: str, index) -> str:
    """Returns the line containing the specified index"""

    line_number = file_text.count('\n', 0, index) + 1
    start_line = file_text.rfind('\n', 0, index) + 1
    end_line = file_text.find('\n', index)
    line = file_text[start_line:end_line].strip()
    return f'{line_number}: {line}'


def process_not_test_case_scenario(file_text: str, index: int, pattern: str) -> tuple[str, str]:
    function_name = get_function_name(index, file_text)
    if function_name + '(' != pattern:
        line = find_matching_lines(file_text, index)
        if not f'def {pattern}' in line:
            return line, function_name
    else:
        return '', ''


def find_pattern_in_functions(directory: Path, pattern: str, n: int) -> list[str]:
    global processed_functions
    polarion_list = []
    function_list = []
    list_of_repeated_definition = []

    if n == 0:
        return polarion_list
    n = n - 1

    print(f"Searching for '{pattern}' in {directory}\n")
    single_files = list(directory.rglob("*.py"))
    escaped_patter = re.escape(pattern)

    for path in single_files:
        file_text = path.read_text(encoding="UTF-8")
        function_definitions = re.findall(fr'def \b{escaped_patter}\b', file_text)
        list_of_repeated_definition.extend(function_definitions)

        if len(list_of_repeated_definition) > 1:
            print('ERROR: There is more than 1 usages of function definition \n')
            return []

        found_elements = list(match.start() for match in re.finditer(escaped_patter, file_text))
        if pattern in file_text:
            if "/test_cases/" in path.as_posix() and path.match("test_*.py"):
                found_polarion_id = search_for_id_pattern(file_text, 'Polarion ID:')
                polarion_list.append(found_polarion_id)
                print(f'TestCase APPROACH\n{path} \n')
                for element in found_elements:
                    line = find_matching_lines(file_text, element)
                    print(line)
            else:
                for index in found_elements:
                    # line, function_list = process_not_test_case_scenario(file_text, index, pattern)
                    # print(f'\nNOT TestCase APPROACH\n{path} \n')
                    # print(line)

                    function_name = get_function_name(index, file_text)
                    if function_name + '(' != pattern:
                        function_list.append(function_name)
                        line = find_matching_lines(file_text, index)
                        if not f'def {pattern}' in line:
                            print(f'\nNOT TestCase APPROACH\n{path} \n')
                            print(line)

    print(f"\nWas found {len(polarion_list)} Polarion ID's with '{pattern}' pattern\n")
    for function in set(function_list):
        if function not in processed_functions:
            processed_functions.add(function)
            print(f"Extending search with '{function}'\n")
            polarion_list.extend(find_pattern_in_functions(directory, function, n))
    return polarion_list


def main(directory: Path, pattern: str, depth: int):
    start = time.time()
    list_of_ids = find_pattern_in_functions(directory, pattern, depth)
    print(set(list_of_ids))
    print(len(set(list_of_ids)))
    end_time = time.time()
    print(end_time - start)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, required=True,
                        help="The pattern what should be looked for in files")
    parser.add_argument("-n", "--number_of_depth", type=int, default=6,
                        help="The depth or the number of recursive calls the function should make.")
    args = parser.parse_args()
    main(directory=args.test_automation_dir, pattern=args.pattern, depth=args.number_of_depth)
