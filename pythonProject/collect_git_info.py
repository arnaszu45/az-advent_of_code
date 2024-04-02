import logging
import argparse
import os
import subprocess
from pathlib import Path
import sys
import re
import json
import time
from typing import Dict

logger = logging.getLogger(__name__)


def is_git_repo(git_repo: Path) -> bool:
    """Takes directory name and checks if it's Git repository"""

    if not git_repo.is_dir():
        logger.error(f"{git_repo} is not a directory")
        return False

    result = subprocess.run(["git", "-C", str(git_repo.resolve()), "rev-parse"], capture_output=True, cwd=git_repo)

    if result.returncode != 0:
        logger.error(f"{git_repo} is not a git repository: \n{' '.join(result.args)}\n{result.stderr}\n")
        return False

    return True


def get_commits(git_repo: Path) -> list[str]:
    """Collects all commit hashes from given Git repository and put them into list"""

    commits = []

    git_log_message = subprocess.run(["git", "log"], capture_output=True, text=True, cwd=git_repo,
                                     encoding="UTF-8")
    if git_log_message.returncode != 0:
        logger.error(f"Error occurred running subprocess:\n{' '.join(git_log_message.args)}\n{git_log_message.stderr}\n")
        return []

    git_log_output = git_log_message.stdout
    lines = git_log_output.splitlines()
    for line in lines:
        if not line.startswith("commit"):
            continue

        _, single_commit_hash, * _ = line.split(" ")
        if len(single_commit_hash) != 40:
            logger.error(f"Expected commit hash to be 40 symbols, got {len(single_commit_hash)}")
            continue

        commits.append(single_commit_hash)
    return commits


def get_author_and_date_from_git_log(commit_log: str) -> tuple[str, str]:
    """Finds and returns 'Author: ' or 'Date: ' from Git log message"""

    author_group = "author"
    date_group = "date"
    match = re.search(fr'Author: (?P<{author_group}>.*)\nDate: (?P<{date_group}>.*)', commit_log)

    if match is None:
        logger.error(f"Could not find {author_group} or {date_group} in log message")
        return "", ""

    author = match.group(author_group)
    date = match.group(date_group)

    return author.strip(), date.strip()


def process_renamed_string(line: str) -> tuple[str, str]:
    """Process the renamed file line, returns full old and new file names"""

    # NOTE: Pattern used for simplifying complex renamed or modified file path into two paths.
    pattern = r'{(.*?)\s*=>\s*(.*?)}'
    old_file, new_file = re.sub(pattern, r'\1', line), re.sub(pattern, r'\2', line)
    return old_file, new_file


def get_changed_and_renamed_files_from_git_log(commit_log: str) -> tuple[str, list, dict[str: str]]:
    """Gets the list of modified file names, old and new renamed file names and the first modified file name"""

    # NOTE: Returns only modified and renamed files, added and removed files cannot be indicated with 'git show'.
    # NOTE: 'first_changed_file' will be used to extract commit message.
    first_changed_file = ""
    modified_files = []
    renamed_files = {}

    for line in commit_log.splitlines():
        if "|" not in line:
            continue

        if not first_changed_file:
            first_changed_file = line.strip()

        cropped_line = line[:line.index("|")].strip()

        # NOTE: "{}", "=>" indicates, that file is renamed, "0" indicates, that it wasn't modified
        if "{" in line and "=>" in line and " 0" in line:
            old_file, new_file = process_renamed_string(cropped_line)
            renamed_files["new_file_name"] = new_file
            renamed_files["old_file_name"] = old_file

        # NOTE: "{}", "=>" indicates, that file is renamed, keeping the new file
        elif "{" in line and "=>" in line:
            _, new_file = process_renamed_string(cropped_line)
            modified_files.append(new_file)
        else:
            modified_files.append(cropped_line)

    return first_changed_file, modified_files, renamed_files


def get_message_from_git_log(commit_log: str, date: str, first_commit_file: str) -> str:
    """Gets the commit message - text between date and first changed file"""

    if not date:
        return ""

    date_index = commit_log.find(date)
    if date_index == -1:
        return ""

    if first_commit_file == "":
        message = commit_log[date_index + len(date):]
        return message.strip()

    message = commit_log[date_index + len(date):commit_log.index(first_commit_file)]

    return message.strip()


def get_insertion_or_deletion_from_git_log(commit_log: str, pattern: str) -> int:
    """Finds and returns 'insertions(+): ' or 'deletions(-)' from Git log message"""
    expected_patterns = ["insertion", "deletion"]

    if pattern not in expected_patterns:
        logger.error(f"Function requires pattern to be {expected_patterns}")
        raise ValueError("Invalid pattern provided. Pattern must be 'insertions' or 'deletions'.")

    match = re.search(rf"(?P<{pattern}>\d+) {pattern}(s)?\(\W\)", commit_log)

    if match is None:
        return 0

    if match.group(pattern) is None:
        return 0

    return int(match.group(pattern))


CommitHash = str
CommitData = Dict[str, str | list[str] | int | dict[str : str]]


def get_commit_info(git_repo: Path) -> Dict[CommitHash, CommitData]:

    all_commits_data: Dict[CommitHash, CommitData] = {}
    commits = get_commits(git_repo)

    if not commits:
        return {}

    for commit_hash in commits:
        # NOTE: '--stat=350' parameter is used to extract whole path, in case it's very long.
        # NOTE: '--date=iso8601' parameter is used to set date formatting, instead using default format.
        info_of_commit = subprocess.run(["git", "show", commit_hash, "--stat=350", "--date=iso8601"],
                                        capture_output=True, encoding="UTF-8", cwd=git_repo)
        if info_of_commit.returncode != 0:
            logger.error(f"Error occurred running subprocess:\n{' '.join(info_of_commit.args)}\n{info_of_commit.stderr}\n")
            return {}

        info_of_commit_output = info_of_commit.stdout

        author, date = get_author_and_date_from_git_log(info_of_commit_output)
        first_line, modified_files, renamed_files = get_changed_and_renamed_files_from_git_log(info_of_commit_output)
        if not first_line:
            logger.warning(f"Commit {commit_hash} does not have modified files")

        commit_data: CommitData = {
                "Commit: ": commit_hash,
                "Author: ": author,
                "Date: ": date,
                "Message: ": get_message_from_git_log(info_of_commit_output, date, first_line),
                'Renamed_files: ': renamed_files,
                "Changed_files: ": modified_files,
                "Insertions: ": get_insertion_or_deletion_from_git_log(info_of_commit_output, "insertion"),
                "Deletions: ": get_insertion_or_deletion_from_git_log(info_of_commit_output, "deletion")
                }

        all_commits_data[f"Commit - {commit_hash}"] = commit_data

    return all_commits_data


def create_json_file(data, json_file_name):
    with open(json_file_name, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--git-repository", type=Path, required=True,
                        help="Specify the path to the git repository directory")
    parser.add_argument("-j", "--json_file", type=Path, default="git_info.json",
                        help="Specify the json file name, where json output will be kept")
    parser.add_argument("-l", "--log-file", default='git_info.log',
                        help="Specify the file name, where logs should be kept")
    return parser.parse_args()


def configure_logger(filename: str) -> logging.Logger:
    logger.setLevel(logging.DEBUG)

    stdout_handle = logging.StreamHandler(sys.stdout)
    file_handle = logging.FileHandler(filename)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    stdout_handle.setFormatter(formatter)
    file_handle.setFormatter(formatter)

    logger.addHandler(stdout_handle)
    logger.addHandler(file_handle)
    return logger


def main(logger: logging.Logger):
    logger.info(" >>> Running the script\n")

    git_repository = is_git_repo(args.git_repository)
    if not git_repository:
        sys.exit(1)

    commits_data = get_commit_info(args.git_repository)
    if not commits_data:
        sys.exit(1)

    try:
        create_json_file(commits_data, args.json_file)
    except Exception as e:
        logger.error(f"Error occurred trying write {args.json_file}: \n{e}")
        sys.exit(1)

    logger.info(f" >>> Was generated {args.json_file} file in {os.getcwd()} directory")


if __name__ == "__main__":
    args = parse_args()
    logger = configure_logger(args.log_file)
    start = time.time()
    main(logger=logger)
    end_time = time.time()
    print(end_time - start)
