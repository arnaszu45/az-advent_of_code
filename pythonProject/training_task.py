from pathlib import Path
import argparse


def search_for_pattern(file_text: str, selected_list: list, pattern: str):
    id_index = file_text.find(pattern)
    if id_index > 0:
        remaining_text = file_text[id_index + len(pattern):]
        remaining_text = remaining_text.split()[0]
        polarion_id = remaining_text.strip()
        selected_list.append(polarion_id)
        return selected_list


def get_function_name(start_pos: int, file_text: str):
    function_starts = file_text.find(' ', start_pos) + 1
    function_ends = file_text.find('(', start_pos) + 1
    return file_text[function_starts:function_ends]


def find_pattern_in_functions(directory: Path, pattern: str, polarion_list: list, n: str):
    n = n - 1
    print(n)
    if n < 0:
        return polarion_list
    print(f"Searching for '{pattern}' in {directory} directory \n")
    single_files = list(directory.rglob("*.py"))
    functions_list = []

    for path in single_files:
        file_text = path.read_text(encoding="UTF-8")
        if '.' + pattern in file_text:  # A way to avoid definition
            if path.match('test_*.py'): # Wrong approach, supposed to look for /test_cases/ folder, not test_
                search_for_pattern(file_text, polarion_list, 'Polarion ID:')
                print(f'TestCase APPROACH \n {path}')
            else:
                print(f'NOT TestCase APPROACH \n {path}')
                index_of_def = file_text.rfind('def ', 0, file_text.find(pattern))
                function_name = get_function_name(index_of_def, file_text)
                functions_list.append(function_name)
    function = functions_list[0]
    find_pattern_in_functions(directory, function, polarion_list, n)

    #     for function in functions_list:
    #         if function == pattern:
    #             a = function

# !!!!!            # find_pattern_in_functions(directory, function, polarion_list)
# cuurent value +1
#if value 6 reetutrn and do nothing


def main(directory: Path, pattern: str):
    polarion_list = []
    find_pattern_in_functions(directory, pattern, polarion_list, 6)
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