from pathlib import Path
import argparse


def main(directory: Path, pattern: str):
    polarion_list = []
    single_files = [path for path in Path(directory).rglob("*.py")]     # All python's files

    for path in single_files:   # Collecting single file's path
        file_text = path.read_text(encoding="UTF-8")    # Making all files readable
        if pattern in file_text:
            id_pattern = 'Polarion ID:'
            if id_pattern in file_text:
                id_index = file_text.find(id_pattern)
                if id_index < 0:
                    continue
                remaining_text = file_text[id_index + len(id_pattern):]
                remaining_text = remaining_text.split()[0]
                polarion_id = remaining_text.strip()
                polarion_list.append(polarion_id)
            else:
                print(file_text.index(pattern))
                res = file_text[:file_text.index(pattern) + len(pattern)]
                indirect_function = res[file_text.index(pattern) - 300:]
                indirect_function =
                print(search_function_name)
                # breakpoint()
    # print(polarion_list)
    print(len(polarion_list))
            # if id_index < 0:
            #     continue
            # remaining_text = file_text[id_index + len(id_pattern):]
            # remaining_text = remaining_text.split()[0]
            # polarion_id = remaining_text.strip()
            # polarion_list.append(polarion_id)
    # print(polarion_list)
    # print(len(polarion_list))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", type=Path, help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, help="The pattern what should be looked for in files")
    args = parser.parse_args()
    main(directory=args.test_automation_dir, pattern=args.pattern)
