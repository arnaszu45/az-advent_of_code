from pathlib import Path
import xml.etree.ElementTree as Et
from copy import deepcopy
import os
import time
import argparse
import traceback


def search_for_setup_name(file_text: str, pattern: str) -> str:
    """Search for specific pattern, returns element after the pattern"""

    setup_index = file_text.find(pattern)
    if setup_index != -1:
        remaining_text = file_text[setup_index + len(pattern):]
        remaining_text = remaining_text.split()[0]
        setup_name = remaining_text.strip()
        return setup_name
    else:
        return ''


def make_dictionary_of_setup_name_and_protocol(filename: Path, directory: Path) -> dict:
    """Collect protocols from XML according to setup name and keeps it in dictionary"""

    dict_of_elements_and_test_type = {}
    tree = Et.parse(filename)
    root = tree.getroot()
    protocols = root.findall('.//protocol')
    for element in protocols:
        test_type = 'unknown'
        script = element.find('test-script-reference').text
        if script[script.find('/test_cases/'): script.find('.py') + 3]:
            test_case_file_name = script[script.find('/test_cases/'): script.find('.py') + 3]  ## Handle random name
            file_name = f'{directory}{test_case_file_name}'  # 4AP2-38092
            full_path = Path(file_name)

            if full_path.exists():
                file_text = full_path.read_text(encoding="UTF-8")
                if 'Title: Semi-automated:' in file_text:
                    test_type = 'semi-automated'
                elif 'Setup: ' in file_text:
                    setup_name = search_for_setup_name(file_text, 'Setup: ')
                    test_type = f'{setup_name.lower()}'
        else:
            print(f"{Et.tostring(element)}\n !!! WARNING, Protocol path is damaged, adding to 'unknown.xml' !!!\n")
        test_case_list = dict_of_elements_and_test_type.get(test_type, [])  # Get is able to return empty list
        test_case_list.append(element)
        dict_of_elements_and_test_type[test_type] = test_case_list

    if len(dict_of_elements_and_test_type) == 1:
        try:
            raise TypeError
        except TypeError:
            print("-- Probably was given wrong 'test_automation' directory -- ")
            traceback.print_exception(quit(), limit=0)

    return dict_of_elements_and_test_type


def distribute_protocols_through_files(filename: Path, dictionary: dict, new_folder: str):
    """Distributes protocols from given XML file into separated new XML files by setup names"""

    try:
        os.makedirs(new_folder)
    except FileExistsError:
        print(f"!!! ERROR: Folder {new_folder} already exists. Use another folder name or delete existing one !!!")
        traceback.print_exception(quit(), limit=0)

    tree = Et.parse(filename)
    root = tree.getroot()

    for key, values in dictionary.items():
        new_root = deepcopy(root)
        new_protocols = new_root.find('.//protocols')
        new_protocols.clear()

        new_protocols.extend(values)

        new_tree = Et.ElementTree(new_root)
        setup_filename = os.path.join(new_folder, f"{key}.xml")
        new_tree.write(setup_filename, encoding='utf-8', xml_declaration=True)


def main(filename: Path, directory: Path, new_folder: str):
    print('--- Running the script ---\n')  # <-- Are prints in here legal?? I mean in main
    dictionary = make_dictionary_of_setup_name_and_protocol(filename, directory)
    distribute_protocols_through_files(filename, dictionary, new_folder)
    amount_of_files_in_directory = len(os.listdir(new_folder))
    print(f'Was generated {amount_of_files_in_directory} new files from {filename}')


if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--xml_file", required=True, type=Path,
                        help="File name or path of xml file which has to be proceeded")
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-n", "--new_folder", required=True, type=str,
                        help="A name of new folder, where xml files will be saved after writing")  # Don't know how to write it nicely
    args = parser.parse_args()
    main(filename=args.xml_file, directory=args.test_automation_dir, new_folder=args.new_folder)
    end_time = time.time()
    print(end_time - start)
