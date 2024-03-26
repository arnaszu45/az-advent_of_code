import logging
import argparse
import subprocess
from pathlib import Path
import sys
import re
import json


def is_git_repo(git_repo: Path) -> bool:
    """Takes directory name and checks if it's Git repository"""

    if not git_repo.is_dir():
        logger.error(f"{git_repo} is not valid directory")
        return False

    result = subprocess.run(["git", "-C", str(git_repo), "rev-parse"])
    if result.returncode != 0:
        logger.error(f"Error: {git_repo} is not a git repository.")
        return False

    return True


def get_commits(git_repo: Path) -> list[str]:
    """Collects all commit hashes from given Git repository and put them into list"""

    commits = []
    git_log_message = subprocess.run(["git", "log"], shell=True, capture_output=True, text=True, cwd=git_repo)
    if git_log_message.returncode == 1:
        logger.error("Command does not exists, please check the subprocess running command")
        return []
    git_log_output = git_log_message.stdout
    lines = git_log_output.splitlines()
    for line in lines:
        if not line.startswith("commit"):
            continue
        _, single_commit_hash, * _ = line.split(" ")  # Checked, commit hash is always 40 symbols
        if len(single_commit_hash) != 40:
            logger.error(f"Commit hash is broken")
            continue
        commits.append(single_commit_hash)
    return commits


def get_author_and_date_from_git_log(commit_log: str) -> tuple[str, str]:
    """Finds and returns 'Author: ' or 'Date: ' from Git log message"""

    match = re.search(r'Author: (?P<author>.*)\nDate: (?P<date>.*)', commit_log)
    if match is None:
        logger.warning("Could not find author or date in log message")
        return "No author", "No date"
    author = match.group('author')
    date = match.group('date')
    return author.strip(), date.strip()


def get_message_from_git_log(commit_hash: str) -> str:
    message = subprocess.run(["git", "show", "-s", "--format=%B", commit_hash], shell=True, capture_output=True,
                             text=True, encoding="UTF-8").stdout
    return message.strip()


def get_file_names_from_git_log(commit_hash: str) -> list[str]:
    file_names_output = subprocess.run(["git", "show", "--pretty=""", "--name-only", commit_hash],
                                       shell=True, capture_output=True, text=True, encoding="UTF-8").stdout
    file_names_list = file_names_output.strip().split('\n')

    return file_names_list


def get_insertion_or_deletion_from_git_log(commit_log: str, pattern: str) -> int:
    """Finds and returns 'insertions(+): ' or 'deletions(-)' from Git log message"""

    if pattern not in ["insertions", "deletions"]:
        logger.error("Function get_insertion_or_deletion_from_git_log requires pattern to be 'insertions' or 'deletions'")

    match = re.search(rf"(\d+) {pattern}\(\W\)", commit_log)
    if match is None:
        logger.warning(f"Could not find any {pattern} in commit log")
        return 0
    return int(match.group(1))


def get_commit_info(git_repo: Path) -> dict:
    all_commits_data = {}
    commits = get_commits(git_repo)
    if not commits:
        return {}
    for commit_hash in commits:
        full_info_of_commit = subprocess.run(["git", "show", commit_hash, "--stat"], shell=True,
                                             capture_output=True, encoding="UTF-8").stdout
        author, date = get_author_and_date_from_git_log(full_info_of_commit)
        commit_data = {
                "Author: ": author,
                "Date: ": date,
                "Message: ": get_message_from_git_log(commit_hash),
                "Changed_files: ": get_file_names_from_git_log(commit_hash),
                "Insertions: ": get_insertion_or_deletion_from_git_log(full_info_of_commit, "insertions"),
                "Deletions: ": get_insertion_or_deletion_from_git_log(full_info_of_commit, "deletions")
                }
        all_commits_data[f"Commit: {commit_hash}"] = commit_data

    return all_commits_data


def create_json_file(data, json_file_name):
    with open(json_file_name, "w") as file:
        json.dump(data, file, indent=4)


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
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    stdout_handle = logging.StreamHandler(sys.stdout)
    file_handle = logging.FileHandler(filename)
    stdout_handle.setFormatter(formatter)
    file_handle.setFormatter(formatter)
    logger.addHandler(stdout_handle)
    logger.addHandler(file_handle)
    return logger


def main(logger: logging.Logger):
    logger.info(" >>> Running the script\n")
    git_repository = is_git_repo(args.git_repository)
    if git_repository is False:
        sys.exit(1)
    commits_data = get_commit_info(args.git_repository)
    if commits_data == {}:
        sys.exit(1)
    create_json_file(commits_data, args.json_file)
    logger.info(" >>> Done")


if __name__ == "__main__":
    args = parse_args()
    logger = configure_logger(args.log_file)
    main(logger=logger)
