import os
import sys
import xml.etree.ElementTree as Et


def find_test_case_name(string: str) -> str:
    start_position = string.find("/test_cases/")
    if start_position == -1:
        print(f'!!! ERROR, given protocol is damaged:\n {string}\n')
        return ''
    else:
        remaining_script = string[start_position:]
        root, ext = os.path.splitext(remaining_script)
        return root + ext


def get_full_name_from_http(element: Et.Element, root: Et.Element):
    sub_element = 'test-script-reference'
    script_reference = element.find(sub_element)
    if script_reference is None:
        print(f'!!! ERROR, given {sub_element} sub element does not exists in given XML file')
        sys.exit(1) # Should it better return '' or exiting is better ??
    if script_reference.text is None:
        print(f'!!! ERROR, given {sub_element} sub element does not exists in given XML file')
        sys.exit(1) # Should it better return '' or exiting is better ??
    if 'href' in script_reference.text:
        # href = element.attrib['href']
        # href = script_reference.attrib['href']
        href = script_reference.find('a') #None
        # href = element.find('a')
        # href = element.findall('a')
        # href = element.get('href') #None
        # href = element.find('a') # None
        # link = href.get('href')
        # href = script_reference.find('a')
        # link = href.get('href') # NoneType' object has no attribute 'get'
        # return href
        return href
    return script_reference.text


# find attribute ['href']


def main():
    xml_file_name = 'test_output.xml'
    tree = Et.parse(xml_file_name)
    root = tree.getroot()
    for element in root.findall(".//protocol"):
        file_name_from_http = get_full_name_from_http(element, root)
        print(file_name_from_http)


main()