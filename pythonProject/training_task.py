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
        else:
            return None


def get_function_name(start_pos: int, file_text: str):
    function_starts = file_text.find(' ', start_pos) + 1
    function_ends = file_text.find('(', start_pos) + 1
    return file_text[function_starts:function_ends]


# def get_indirect_functions(directory: Path, pattern: str, selected_list: list):
#     all_paths = list(directory.rglob("*.py"))
#     for path in all_paths:
#         file_text = path.read_text(encoding="UTF-8")
#         if pattern in file_text:
#             if search_for_pattern(file_text, selected_list, 'Polarion ID:') is None:
#                 index_of_function = file_text.rfind('def', 0, file_text.find(pattern))
#                 indirect_function = get_function_name(index_of_function, file_text)
#                 indirect_function = list(indirect_function.split())
#                 return


def main(directory: Path, pattern: str):
    polarion_list = []
    single_files = list(directory.rglob("*.py"))
    for path in single_files:
        file_text = path.read_text(encoding="UTF-8")
        # get_indirect_functions(directory, pattern, polarion_list)

        if pattern in file_text:
            if search_for_pattern(file_text, polarion_list, 'Polarion ID:') is None:
                index_of_def = file_text.rfind('def', 0, file_text.find(pattern))
                indirect_function = get_function_name(index_of_def, file_text)
                print(indirect_function)




#             if id_pattern in file_text:
#                 id_index = file_text.find(id_pattern)
#                 if id_index < 0:
#                     continue
#                 remaining_text = file_text[id_index + len(id_pattern):]
#                 remaining_text = remaining_text.split()[0]
#                 polarion_id = remaining_text.strip()
#                 polarion_list.append(polarion_id)
#             else:
#                 res = file_text[:file_text.index(pattern) + len(pattern)]
#                 indirect_function = res[file_text.index(pattern) - 300:]
                # indirect_function =
                # print(search_function_name)
    print(polarion_list)
    print(len(polarion_list))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", type=Path, help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, help="The pattern what should be looked for in files")
    args = parser.parse_args()
    main(directory=args.test_automation_dir, pattern=args.pattern)
