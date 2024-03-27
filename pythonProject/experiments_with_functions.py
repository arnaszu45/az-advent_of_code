import re

string = """
commit abc7659fec568cd0275aca143001a7493b0527ed
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   Mon Feb 19 13:45:32 2024 +0200

    Commint code of advent of code first taskfvndsjvbndsjkb fvsdfcjfbjdskfnjsdfnsdjkfnjsdkfb jsdkf bjsdfbsjdvbnsf
    ddnjdcbwebewjdwk

 pythonProject/.idea/.gitignore                     |    3 +
 .../.idea/inspectionProfiles/profiles_settings.xml |    6 +
 pythonProject/.idea/misc.xml                       |    7 +
 pythonProject/.idea/modules.xml                    |    8 +
 pythonProject/.idea/pythonProject.iml              |   10 +
 pythonProject/.idea/vcs.xml                        |    6 +
 pythonProject/advent_of_code_1.py                  |   21 +
 pythonProject/advent_of_code_1_input               | 1000 ++++++++++++++++++++
 8 files changed, 1061 insertions(+)
"""


def get_file_names_from_git_log(commit_log: str) -> list[str]:
    """Gets the list of file names changed in a commit specified by its hash"""

    file_names = []
    for line in commit_log.splitlines():
        if "|" not in line:
            continue

        index = line.find("|")
        if index == -1:
            continue

        file_name = line[:index].strip()
        file_names.append(file_name)

    return file_names


print(get_file_names_from_git_log(string))


def get_message_from_git_log(commit_log: str) -> str:
    """Gets the commit message for a given commit log"""

    match = re.search(r'\n\n(?P<message>.*?)\n\n', commit_log)
    if match is None:
        print('ERROR')
        return ""

    return match.group('message').strip()


print(get_message_from_git_log(string))