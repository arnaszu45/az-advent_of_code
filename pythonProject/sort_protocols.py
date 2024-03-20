import unicodedata
from pathlib import Path
import xml.etree.ElementTree as Et
from copy import deepcopy
import os
import time
import argparse
import sys
import logging
from enum import Enum, auto
import glob


class Errors(Enum):
    XML_ERROR = auto()
    XML_ERROR_WRITING = auto()  # Learn stuff bout Enum and how to use it


def parse_xml_file(xml_file_name: Path) -> Et.Element:
    """"Parses given XML file and returns root and specified SubElement """  # Not testable

    try:
        tree = Et.parse(xml_file_name)
    except Et.ParseError as e:
        logger.error(f'Can not parse this XML file, error message: !!!\n{e}')
        sys.exit(1)
    root = tree.getroot()
    return root


def search_for_setup_name(file_text: str, pattern: str) -> str:
    """Search for specific pattern, returns element after the pattern"""  # Need UnitTest

    setup_index = file_text.find(pattern)
    if setup_index != -1:
        remaining_text = file_text[setup_index + len(pattern):]
        remaining_text = remaining_text.split()[0]
        setup_name = remaining_text.strip()
        return setup_name
    else:
        return ''


def get_sub_element_text_from_protocol(element: Et.Element):
    """Takes Et.Element and look for specific Sub Element, returns its text"""  # Not testable

    sub_element = 'test-script-reference'
    script_reference = element.find(sub_element)

    if script_reference is None:
        logger.error(f"Given {sub_element} sub element does not exists in given XML file")
        return ""
    if script_reference.text is None:
        logger.error(f"Given {sub_element} sub element does not exists in given XML file")
        return ""
    return script_reference.text


def get_full_http_name(script: str) -> str:
    """Collects and returns full link of the file"""  # Need UnitTest

    clean_et_element = unicodedata.normalize("NFKD", script)  # Actually it does not do anything at this moment
    start_position = clean_et_element.rfind('http')  # Href has https
    if start_position == -1:
        logger.warning(f"There is no 'http' inside --> {script}")
        return ""
    end_position = clean_et_element.rfind('.')  # Results good, better for different extensions than .py
    if end_position == -1:
        logger.warning(f"There is no '.' inside --> {script}")
        return ""
    return clean_et_element[start_position:end_position]


def find_test_case_name(string: str) -> str:  # Can be joined with get_full_http_name, one function for file name
    """Search in full link for /test_case/ pattern and returns file name"""  # Need UnitTest

    start_position = string.find("/test_cases/")
    if start_position == -1:
        logger.warning(f"Protocol is damaged. There is no '/test_cases/' inside --> {string}")
        return ""
    else:
        remaining_script = string[start_position:]
        return remaining_script


def select_name_of_test_type(file_text: str) -> str:  # Need UnitTest
    """Identify test type of test case and returns its name"""

    if 'Title: Semi-automated:' in file_text:
        return 'semi-automated'
    elif 'Setup: ' in file_text:
        setup_name = search_for_setup_name(file_text, 'Setup: ')
        return f'{setup_name.lower()}'
    return ""


def categorise_protocols_by_setup(test_automation_dir: Path, root: Et.Element) -> dict:
    """Collects protocols from XML file, categorise by setup name and keeps it in dictionary"""

    dict_of_elements_and_test_type: dict[str, list[Et.Element]] = {}
    for element in root.findall(".//protocol"):
        test_type = "unknown"

        http_name = get_full_http_name(get_sub_element_text_from_protocol(element))
        path = find_test_case_name(http_name)
        file = glob.glob(f"{test_automation_dir}{path}.*")  # Returns list of one element
        if not file:
            logger.warning(f"File does not exists --> {path}")
        else:
            existing_file = Path(file[0])
            file_text = existing_file.read_text(encoding="UTF-8")
            test_type = select_name_of_test_type(file_text)
        test_case_list = dict_of_elements_and_test_type.get(test_type, [])
        test_case_list.append(element)
        dict_of_elements_and_test_type[test_type] = test_case_list

    if len(dict_of_elements_and_test_type) == 1 and dict_of_elements_and_test_type["unknown"]:
        logger.error("Files consists only of 'unknown' test type, cancelling !!!")
        sys.exit(1)
    return dict_of_elements_and_test_type


def distribute_protocols_through_files(setup_name_and_protocol: dict, output_folder: str, root: Et.Element):
    """Distributes protocols from given XML file into separated new XML files by setup names"""

    new_root = deepcopy(root)
    pattern = './/protocols'
    new_protocols = new_root.find(pattern)
    if new_protocols is None:
        logger.error(f"!!! ERROR: '{pattern}' does not exists in XML root")
        sys.exit(1)

    try:
        os.makedirs(output_folder)
    except FileExistsError:
        logger.error(f"Folder {output_folder} already exists. Use another folder name or delete existing one!")
        sys.exit(1)

    for key, values in setup_name_and_protocol.items():
        new_protocols.clear()
        new_protocols.extend(values)
        new_tree = Et.ElementTree(new_root)
        setup_filename = os.path.join(output_folder, f"{key}.xml")
        new_tree.write(setup_filename, encoding='utf-8', xml_declaration=True)


def main(export_file_name: Path, test_automation_dir: Path, output_folder: str, logger: logging.Logger):
    logger.info("Running the script\n")
    root = parse_xml_file(export_file_name)
    protocols_by_setup = categorise_protocols_by_setup(test_automation_dir, root)
    distribute_protocols_through_files(protocols_by_setup, output_folder, root)
    amount_of_files_in_directory = len(os.listdir(output_folder))
    logger.info(f"Was generated {amount_of_files_in_directory} new files from {export_file_name}")


def configure_logger(filename: str) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s - %(message)s")
    file_handler = logging.FileHandler(filename)
    stdout_handle = logging.StreamHandler(sys.stdout)
    stdout_handle.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handle)
    return logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--xml_file", required=True, type=Path,
                        help="File name or path of xml file which has to be proceeded")
    parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
                        help="Directory of test automation folder")
    parser.add_argument("-o", "--output_folder", required=True, type=Path,
                        help="A name of new folder, where xml files will be saved after writing")
    parser.add_argument("-l", "--log_file", required=True, type=Path,
                        help="Log path")

    args = parser.parse_args()
    logger = configure_logger(args.log_file)
    start = time.time()
    main(export_file_name=args.xml_file, test_automation_dir=args.test_automation_dir,
         output_folder=args.output_folder, logger=logger)
    end_time = time.time()
    print(end_time - start)
