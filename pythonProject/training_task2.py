from pathlib import Path
import xml.etree.ElementTree as Et
import re
import argparse
from copy import deepcopy


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


# def create_new_sorted_file(root: Et.Element, element: Et.Element):
#     new_root = deepcopy(root)
#     new_protocols = new_root.find('.//protocols')
#     new_protocols.clear()


def main(filename: str, directory: str):
    tree = Et.parse(filename)
    root = tree.getroot()
    protocols = root.findall('.//protocol')
    for element in protocols:
        script = element.find('.//test-script-reference').text
        path = script[script.find('test_cases/'): script.find('.py') + 3]
        filename = Path(directory + '/' + path)
        if filename.exists():
            file_text = filename.read_text(encoding="UTF-8")
            if 'Title: Semi-automated:' in file_text:
                filename = 'semi_automated.xml'
            elif 'Setup: ' in file_text:
                setup_name = search_for_setup_name(file_text, 'Setup: ')
                filename = f'{setup_name.lower()}.xml'
        else:
            filename = 'unknown.xml'

        copied_tree = deepcopy(tree)
        new_root = deepcopy(root)
        new_protocols = new_root.find('.//protocols')
        new_protocols.clear()
        new_tree = Et.ElementTree(new_root)
        new_tree.write(filename, encoding='utf-8', xml_declaration=True)
        break

        # protocols_in_copied_file = copied_tree.find('.//protocols')
        # protocols_in_copied_file.append(element)
        # copied_tree.write(filename, encoding="UTF-8", xml_declaration=True)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-f", "--xml_file", required=True, type=Path,
    #                     help="File name or path of xml file which has to be proceed")
    # parser.add_argument("-d", "--test_automation_dir", required=True, type=Path,
    #                     help="Directory of test automation folder")

    # args = parser.parse_args()
    export_file = "export.xml"
    test_automation_dir = 'TestAutomation'
    main(export_file, test_automation_dir)
