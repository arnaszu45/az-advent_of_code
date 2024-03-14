from pathlib import Path
import xml.etree.ElementTree as Et
from copy import deepcopy
import os
import time
import argparse


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


def make_dictionary_of_setup_name_and_protocol(filename: str, directory: str) -> dict:
    """Collect protocols from XML according to setup name and keeps it in dictionary"""

    dict_of_elements_and_test_type = {}
    tree = Et.parse(filename)
    root = tree.getroot()
    protocols = root.findall('.//protocol')
    for element in protocols:
        script = element.find('.//test-script-reference').text
        path = script[script.find('test_cases/'): script.find('.py') + 3]   ## Also modify here
        file_name = Path(directory + '/' + path)                            ## Fix this part 4AP2-38092
        test_type = 'unknown'
        if file_name.exists():
            file_text = file_name.read_text(encoding="UTF-8")
            if 'Title: Semi-automated:' in file_text:
                test_type = 'semi-automated'
            elif 'Setup: ' in file_text:
                setup_name = search_for_setup_name(file_text, 'Setup: ')
                test_type = f'{setup_name.lower()}'

        test_case_list = dict_of_elements_and_test_type.get(test_type, [])  # Get is able to return empty list
        test_case_list.append(element)
        dict_of_elements_and_test_type[test_type] = test_case_list

    return dict_of_elements_and_test_type


def distribute_protocols_through_files(filename: str, dictionary: dict):
    """Distributes protocols from given XML file into separated new XML files by setup names"""

    os.makedirs('output', exist_ok=True)

    tree = Et.parse(filename)
    root = tree.getroot()

    for key, values in dictionary.items():
        new_root = deepcopy(root)
        new_protocols = new_root.find('.//protocols')
        new_protocols.clear()

        new_protocols.extend(values)

        new_tree = Et.ElementTree(new_root)
        setup_filename = os.path.join('output', f"{key}.xml")
        new_tree.write(setup_filename, encoding='utf-8', xml_declaration=True)


def main(filename: str, directory: str):            # Need some prints about running the script
    dictionary = make_dictionary_of_setup_name_and_protocol(filename, directory)
    distribute_protocols_through_files(filename, dictionary)


if __name__ == '__main__':
    start = time.time()
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-f", "--xml_file", required=True, type=Path,
    #                     help="File name or path of xml file which has to be proceeded")
    # parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,  # Not correct will look for another approach
    #                     help="Directory of test automation folder")
    #
    # args = parser.parse_args()
    # main(filename=args.xml_file, directory=args.test_automation_dir)

    export_file = "export.xml"              # Add argparse
    test_automation_dir = 'TestAutomation'   # Add argparse
    main(export_file, test_automation_dir)

    end_time = time.time()
    print(end_time - start)
