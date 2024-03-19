from pathlib import Path
import xml.etree.ElementTree as Et
from copy import deepcopy
import os
import time
import argparse
import sys
import logging
from enum import Enum, auto
logger = logging.getLogger(__name__)


class Errors(Enum):
    XML_ERROR = auto()
    XML_ERROR_WRITING = auto()  # Learn stuff bout Enum and how to use it


def parse_xml_file(xml_file_name: Path):
    """"Parses given XML file and returns root and specified SubElement """

    try:
        tree = Et.parse(xml_file_name)
    except Et.ParseError as e:
        logger.error(f'Can not parse this XML file, error message: !!!\n{e}')
        sys.exit(1)
    root = tree.getroot()
    return root


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


def get_full_name_from_http(element: Et.Element) -> str:
    """Collects and returns full link of the file"""

    sub_element = 'test-script-reference'
    script_reference = element.find(sub_element)

    if script_reference is None:
        print(f'!!! ERROR, given {sub_element} sub element does not exists in given XML file')
        logger.error(f'Given {sub_element} sub element does not exists in given XML file')
        sys.exit(1) # Should it better return '' or exiting is better ??
    if script_reference.text is None:
        print(f'!!! ERROR, given {sub_element} sub element does not exists in given XML file')
        logger.error(f'Given {sub_element} sub element does not exists in given XML file')
        sys.exit(1) # Should it better return '' or exiting is better ??

    script = script_reference.text
    if 'href' in script:  # Need another approach, testing
        script = script[script.find('>') + 1: script.rfind('<')]  # Need another approach, testing

    return script


def find_test_case_name(string: str) -> str:
    """Search in full link for /test_case/ pattern and returns file name"""

    start_position = string.find("/test_cases/")
    if start_position == -1:
        print(f'!!! WARNING, given protocol is damaged:\n {string}\n')
        logger.warning(f"Given protocol is damaged:\n {string}\n")
        return ''
    else:
        remaining_script = string[start_position:]
        root, ext = os.path.splitext(remaining_script)
        return root + ext


def select_name_of_test_type(full_path: Path) -> str:
    """Identify test type of test case and returns its name"""

    file_text = full_path.read_text(encoding="UTF-8")
    if 'Title: Semi-automated:' in file_text:
        return 'semi-automated'
    elif 'Setup: ' in file_text:
        setup_name = search_for_setup_name(file_text, 'Setup: ')
        return f'{setup_name.lower()}'


def categorise_protocols_by_setup(test_automation_dir: Path, root: Et.Element) -> dict:
    """Collects protocols from XML file, categorise by setup name and keeps it in dictionary"""

    dict_of_elements_and_test_type = {}
    for element in root.findall(".//protocol"):
        test_type = "unknown"

        file_name = get_full_name_from_http(element)
        path = find_test_case_name(file_name)
        full_path = Path(f'{test_automation_dir}{path}')
        if full_path.exists() and path != "":
            test_type = select_name_of_test_type(full_path)
        else:
            print(f"{path}\n!!! WARNING, File does not exists, adding to 'unknown.xml' !!!\n")
            logger.warning(f"{path}\nFile does not exists, adding to 'unknown.xml' !!!\n")
        test_case_list = dict_of_elements_and_test_type.get(test_type, [])
        test_case_list.append(element)
        dict_of_elements_and_test_type[test_type] = test_case_list

    if len(dict_of_elements_and_test_type) == 1 and dict_of_elements_and_test_type["unknown"]:
        print("!!! ERROR, files consists only of 'unknown' test type, cancelling !!! ")
        logger.error("Files consists only of 'unknown' test type, cancelling !!!")
        sys.exit(1)
    return dict_of_elements_and_test_type


def distribute_protocols_through_files(setup_name_and_protocol: dict, output_folder: str, root: Et.Element):
    """Distributes protocols from given XML file into separated new XML files by setup names"""

    new_root = deepcopy(root)
    pattern = './/protocols'
    new_protocols = new_root.find(pattern)
    if new_protocols is None:
        print(f"!!! ERROR: '{pattern}' does not exists in XML root")
        logger.error(f"!!! ERROR: '{pattern}' does not exists in XML root")  # Ummm not sure how to correctly give this information
        sys.exit(1)

    try:
        os.makedirs(output_folder)
    except FileExistsError:
        print(f"!!! ERROR: Folder {output_folder} already exists. Use another folder name or delete existing one !!!")
        logger.error(f"Folder {output_folder} already exists. Use another folder name or delete existing one!")
        sys.exit(1)

    for key, values in setup_name_and_protocol.items():
        new_protocols.clear()
        new_protocols.extend(values)
        new_tree = Et.ElementTree(new_root)
        setup_filename = os.path.join(output_folder, f"{key}.xml")
        new_tree.write(setup_filename, encoding='utf-8', xml_declaration=True)


def main(export_file_name: Path, test_automation_dir: Path, output_folder: str):
    logging.basicConfig(filename="sorting.log", level=logging.INFO)
    logger.info("Running the script\n")
    print("--- Running the script ---")  # IF I use logging ,should I keep prints ????
    root = parse_xml_file(export_file_name)
    protocols_by_setup = categorise_protocols_by_setup(test_automation_dir, root)
    distribute_protocols_through_files(protocols_by_setup, output_folder, root)
    amount_of_files_in_directory = len(os.listdir(output_folder))
    logger.info(f"Was generated {amount_of_files_in_directory} new files from {export_file_name}")
    print(f"Was generated {amount_of_files_in_directory} new files from {export_file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--xml_file", required=True, type=Path,
                        help="File name or path of xml file which has to be proceeded")
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-n", "--new_folder", required=True, type=Path,
                        help="A name of new folder, where xml files will be saved after writing")
    args = parser.parse_args()
    start = time.time()
    main(export_file_name=args.xml_file, test_automation_dir=args.test_automation_dir, output_folder=args.new_folder)
    end_time = time.time()
    print(end_time - start)
