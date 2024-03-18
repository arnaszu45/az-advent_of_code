from pathlib import Path
import xml.etree.ElementTree as Et
from copy import deepcopy
import os
import time
import argparse
import sys


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


def find_test_case_start(string: str):
    """Finds the index where given pattern begins, if it's not exists - returns -1 """

    start_position = string.find("/test_cases/")
    if start_position != -1:
        return start_position
    else:
        return -1


def get_full_name_from_http(element: Et.Element):
    sub_element = 'test-script-reference'
    script_reference = element.find(sub_element)
    if script_reference is None:
        print(f'!!! ERROR, given {sub_element} sub element does not exists in given XML file')
        sys.exit()
    script = script_reference.text.strip()

    if 'href' in script:
        script = script[script.find('>') + 1: script.rfind('<')]

    if script.startswith('http'):
        return script
    else:
        print(f'!!! ERROR, {sub_element} sub element does not contain a valid URL starting with "http"')
        sys.exit()


def find_test_case_file_name(full_protocol: Et.Element):
    script_reference = full_protocol.find('test-script-reference')
    print(script_reference)
    ## handle a elemnt, grab href

    # if script_reference is None:
    #     return file_name
    # script = script_reference.text
    # start_position = find_test_case_start(script)
    # if start_position == -1:
    #     return file_name
    # remaining_script = script[start_position:]
    # path, ext = os.path.splitext(remaining_script)
    # print(path, ext)



def categorise_protocols_by_setup(directory: Path, root: Et.Element) -> dict:
    """Collects protocols from XML file, categorise by setup name and keeps it in dictionary"""

    dict_of_elements_and_test_type = {}
    for element in root.findall(".//protocol"):
        test_type = "unknown"
        find_test_case_file_name(element)
        # script = element.find('test-script-reference').text
        # if script[script.find('/test_cases/'): script.find('.py') + 3]:
        #     test_case_file_name = script[script.find('/test_cases/'): script.find('.py') + 3]
        #     file_name = f'{directory}{test_case_file_name}'  # 4AP2-38092
        #     full_path = Path(file_name)

        #     if full_path.exists():
        #         file_text = full_path.read_text(encoding="UTF-8")
        #         if 'Title: Semi-automated:' in file_text:
        #             test_type = 'semi-automated'
        #         elif 'Setup: ' in file_text:
        #             setup_name = search_for_setup_name(file_text, 'Setup: ')
        #             test_type = f'{setup_name.lower()}'
        # else: # Fix here, do everything above
        #     print(f"{script}\n !!! WARNING, Protocol path is damaged, adding to 'unknown.xml' !!!\n") # do if not above instead of going down
        # test_case_list = dict_of_elements_and_test_type.get(test_type, [])  # Get is able to return empty list
        # test_case_list.append(element)
        # dict_of_elements_and_test_type[test_type] = test_case_list

    if len(dict_of_elements_and_test_type) == 1:
        print("-- Probably was given wrong 'test_automation' directory -- ")
        sys.exit()

    return dict_of_elements_and_test_type


def distribute_protocols_through_files(setup_name_and_protocol: dict, output_folder: str, root: Et.Element):
    """Distributes protocols from given XML file into separated new XML files by setup names"""

    new_root = deepcopy(root)
    pattern = './/protocols'
    new_protocols = new_root.find(pattern)
    if new_protocols is None:
        print(f"!!! ERROR: '{pattern}' does not exists in XML root")  # Ummm not sure how to correctly give this information
        sys.exit()

    try:
        os.makedirs(output_folder)
    except FileExistsError:
        print(f"!!! ERROR: Folder {output_folder} already exists. Use another folder name or delete existing one !!!")  # All prints has to be changed into logs
        sys.exit()

    for key, values in setup_name_and_protocol.items():
        new_protocols.clear()
        new_protocols.extend(values)
        new_tree = Et.ElementTree(new_root)
        setup_filename = os.path.join(output_folder, f"{key}.xml")
        new_tree.write(setup_filename, encoding='utf-8', xml_declaration=True)


def parse_xml_file(xml_file_name: Path):
    """"Parses given XML file and returns root and specified SubElement """

    try:
        tree = Et.parse(xml_file_name)
        root = tree.getroot()   # BAD BAD BAD
        return root
    except Et.ParseError as e:
        print(f'!!! ERROR, can not parse this XML file, error message: !!!\n{e}')
        sys.exit()


def main(export_file_name: Path, test_automation_dir: Path, output_folder: str):
    print('--- Running the script ---\n')  # <-- Make logs
    root = parse_xml_file(export_file_name)
    protocols_by_setup = categorise_protocols_by_setup(test_automation_dir, root)
    distribute_protocols_through_files(protocols_by_setup, output_folder, root)
    amount_of_files_in_directory = len(os.listdir(output_folder))
    print(f'Was generated {amount_of_files_in_directory} new files from {export_file_name}')


if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--xml_file", required=True, type=Path,
                        help="File name or path of xml file which has to be proceeded")
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-n", "--new_folder", required=True, type=Path,
                        help="A name of new folder, where xml files will be saved after writing")
    args = parser.parse_args()
    main(export_file_name=args.xml_file, test_automation_dir=args.test_automation_dir, output_folder=args.new_folder)
    end_time = time.time()
    print(end_time - start)
