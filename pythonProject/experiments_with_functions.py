import re
import subprocess
import json

string = """
commit ddcb0a844d2bfcc6b76469bcb369eb14babb2766
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   Tue Feb 20 10:37:25 2024 +0200

    Commititng second task ,the answer is correct, will be waiting for the review

 pythonProject/advent_of_code_2.py | 29 +++++++++++++----------------
 1 file changed, 13 insertions(+), 16 deletions(-)
"""


def get_author_from_git_log(commit_log: str) -> str:
    """Finds and returns 'Author' from Git log message"""

    match = re.search(r"Author: (.+)", commit_log)
    if match is None:
        return ""
    return match.group(1).strip()


def get_date_from_git_log(commit_log: str) -> str:
    """Finds and returns 'Date' from Git log message"""

    match = re.search(r"Date: (.+)", commit_log)
    if match is None:
        return ""
    return match.group(1).strip()


def get_message_from_git_log(commit_hash: str) -> str:
    message = subprocess.run(["git", "show", "-s", "--format=%B", commit_hash], shell=True, capture_output=True,
                             text=True, encoding="UTF-8").stdout
    return message.strip()


def get_file_names_from_git_log(commit_hash: str) -> str:
    file_name = subprocess.run(["git", "show", "--pretty=""", "--name-only", commit_hash],
                               shell=True, capture_output=True, text=True, encoding="UTF-8").stdout
    return file_name.strip()


def get_insertions_from_git_log(commit_log: str) -> str:
    pattern = r"\d+.insertions\(\+\)"
    match = re.search(pattern, commit_log)
    if match is None:
        return "0 insertions(+)"
    return match.group()


def get_deletions_from_git_log(commit_log: str) -> str:
    pattern = r"\d+.deletions\(\-\)"
    match = re.search(pattern, commit_log)
    if match is None:
        return "0 deletions(-)"
    return match.group()


commit_hash = "Ecdwsxsd4444"
data = {
        f"Commit_hash : {commit_hash}": {
            "Author: ": get_author_from_git_log(string),
            "Date: ": get_date_from_git_log(string),
            "Insertions: ": get_insertions_from_git_log(string),
            "Deletions: ": get_deletions_from_git_log(string)
        }
}

with open("git_info_exp.json", "w") as f:
    json.dump(data, f, indent=4)