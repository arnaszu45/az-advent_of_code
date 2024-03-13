from pathlib import Path
import xml.etree.ElementTree as Et
from copy import deepcopy
import os
import time


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


def make_dictionary_of_setup_name_and_protocol(filename: str, directory: str) -> tuple[dict, set]:
    """Collect protocols from XML according to setup name and keeps it in dictionary"""

    list_setup_names = []
    dict_of_elements_and_setup = {}
    tree = Et.parse(filename)
    root = tree.getroot()
    protocols = root.findall('.//protocol')
    for element in protocols:
        script = element.find('.//test-script-reference').text
        path = script[script.find('test_cases/'): script.find('.py') + 3]
        file_name = Path(directory + '/' + path)
        if file_name.exists():
            file_text = file_name.read_text(encoding="UTF-8")
            if 'Title: Semi-automated:' in file_text:
                filename = 'semi-automated'
                list_setup_names.append(filename)
            elif 'Setup: ' in file_text:
                setup_name = search_for_setup_name(file_text, 'Setup: ')
                filename = f'{setup_name.lower()}'
                list_setup_names.append(filename)
        else:
            filename = 'unknown'
        list_setup_names.append(filename)
        dict_of_elements_and_setup.update({element: filename})
    return dict_of_elements_and_setup, set(list_setup_names)


def distribute_protocols_through_files(filename: str, dictionary: dict, setup_names: set):
    """Distributes protocols from given XML file into separated new XML files by setup names"""

    os.makedirs('output', exist_ok=True)

    tree = Et.parse(filename)   # Could these lines be kept in function ???
    root = tree.getroot()       # Could these lines be kept in function ???

    for setup_name in setup_names:
        new_root = deepcopy(root)
        new_protocols = new_root.find('.//protocols')
        new_protocols.clear()

        for protocol, name in dictionary.items():
            if setup_name == name:
                new_protocols.append(deepcopy(protocol))
                new_tree = Et.ElementTree(new_root)
                setup_filename = os.path.join('output', f"{setup_name}.xml")
                new_tree.write(setup_filename, encoding='utf-8', xml_declaration=True)


def main(filename: str, directory: str):            # Need some prints about running the script
    dictionary, setup_names = make_dictionary_of_setup_name_and_protocol(filename, directory)
    distribute_protocols_through_files(filename, dictionary, setup_names)


if __name__ == '__main__':
    start = time.time()
    export_file = "export.xml"              # Add argparse
    test_automation_dir = 'TestAutomation'   # Add argparse
    main(export_file, test_automation_dir)
    end_time = time.time()
    print(end_time - start)
