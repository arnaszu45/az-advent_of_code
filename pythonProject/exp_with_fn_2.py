import os
import sys
import xml.etree.ElementTree as Et


def find_test_case_start(string: str):
    start_position = string.find("/test_cases/")
    if start_position != -1:
        return start_position
    else:
        return -1


def find_test_case_name(start_position: int, string: str):
    if start_position == -1:
        print('well, FAILED FAILED FAILED')
        sys.exit()
    else:
        remaining_script = string[start_position:]
        path, ext = os.path.splitext(remaining_script)
        return path, ext


def get_full_name_from_http(element: Et.Element):
    script_reference = element.find('test-script-reference')
    if script_reference is None:
        print('FAILED FAILED FAILED')
        sys.exit()
    if 'href' in script_reference.text:
        script = script_reference.text
        return script[script.find('>') + 1: script.rfind('<')]
    else:
        return script_reference.text


def main():
    xml_file_name = 'test_output.xml'
    tree = Et.parse(xml_file_name)
    root = tree.getroot()
    for element in root.findall(".//protocol"):
        file_name_from_http = get_full_name_from_http(element)
        start = find_test_case_start(file_name_from_http)
        print(find_test_case_name(start, file_name_from_http))
main()