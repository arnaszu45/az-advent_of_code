from pathlib import Path
import argparse
from ipdb import set_trace


def search_for_pattern(file_text: str, selected_list: list, pattern: str):
    id_index = file_text.find(pattern)
    if id_index > 0:
        remaining_text = file_text[id_index + len(pattern):]
        remaining_text = remaining_text.split()[0]
        polarion_id = remaining_text.strip()
        print(polarion_id)
        selected_list.append(polarion_id)
        return selected_list

def get_function_name(start_pos: int, file_text: str):
    function_starts = file_text.rfind('def ', 0, start_pos) + len('def ')
    function_ends = file_text.find('(', function_starts)
    return file_text[function_starts:function_ends]

# def get_function_name(start_pos: int, file_text: str):
#     function_starts = file_text.find(' ', start_pos) + 1
#     function_ends = file_text.find('(', start_pos)
#     return file_text[function_starts:function_ends]


def find_pattern_in_functions(directory: Path, pattern: str, polarion_list: list, n: int):

    if n == 0:
        return polarion_list
    n = n - 1

    print(f"Searching for '{pattern}' in {directory} directory \n")
    single_files = list(directory.rglob("*.py"))
    functions_list = []

    for path in single_files:
        file_text = path.read_text(encoding="UTF-8")
        for i, line in enumerate(file_text.splitlines()):
            if pattern in line:
                line = line.strip()
                if "/test_cases/" in path.as_posix() and path.match("test_*.py"):

                    if not line.startswith('def '):
                        if '_' + pattern not in line:
                            search_for_pattern(file_text, polarion_list, 'Polarion ID:')
                            print(f'TestCase APPROACH \n{path} \n{i}:    {line}\n')

                elif not line.startswith('def '):
                    print(f'NOT TestCase APPROACH \n{path} \n{line.strip()} \n')
                    index_of_def = file_text.index(line)
                    function_name = get_function_name(index_of_def, file_text)
                    functions_list.append(function_name)
    #             else:
    #                 index_of_def = file_text.rfind('def ', 0, file_text.rfind(pattern))
    #                 function_name = get_function_name(index_of_def, file_text)
    #                 if function_name != pattern:
    #                     functions_list.append(function_name)
    #
    print(functions_list)
    function = functions_list[0]
    set_trace()
    find_pattern_in_functions(directory, function, polarion_list, n)


def main(directory: Path, pattern: str):
    polarion_list = []
    find_pattern_in_functions(directory, pattern, polarion_list, 3)
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