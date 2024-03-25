import logging
import argparse
import subprocess
from pathlib import Path
import sys
import re


def is_git_repo(git_repo: Path):
    """Takes directory name and checks if it's Git repository"""

    if not git_repo.is_dir():
        logger.error(f"{git_repo} is not valid directory")

    result = subprocess.run(["git", "-C", str(git_repo), "rev-parse"])
    if result.returncode != 0:
        logger.error(f"Error: {git_repo} is not a git repository.")
    return "Given repository is valid"


def get_commits(git_repo: Path) -> list[str]:  # here text = true must, otherwise it returns bytes
    """Collects all commit hashes from given Git repository and put them into list"""

    commits = []
    git_log_output = subprocess.run(["git", "log"], shell=True, capture_output=True, text=True,
                                    cwd=git_repo).stdout
    lines = git_log_output.splitlines()
    for line in lines:
        if line.startswith("commit"):
            line_parts = len(line.split(" "))
            if line_parts != 2:
                logger.warning(f"Commit line consists not of 2 parts -> {line}")
                continue
            single_commit = line.split(" ")[1]
            commits.append(single_commit)
    return commits


def get_author_from_git_log(commit_log: str) -> str:
    """Finds and returns 'Author' from Git log message"""

    match = re.search(r"Author: (.+)", commit_log)
    if match is None:
        logger.warning("Could not find Author in commit log")
        return ""
    return match.group(1).strip()


def get_date_from_git_log(commit_log: str) -> str:
    """Finds and returns 'Date' from Git log message"""

    match = re.search(r"Date: (.+)", commit_log)
    if match is None:
        logger.warning("Could not find Date in commit log")
        return ""
    return match.group(1).strip()


def get_message_from_git_log(commit_hash: str) -> str:
    message = subprocess.run(["git", "show", "-s", "--format=%B", commit_hash], shell=True, capture_output=True,
                             text=True, encoding="UTF-8").stdout
    return message.strip()


def get_file_names_from_git_log(commit_hash: str) -> str:
    file_name = subprocess.run(["git", "show", "--pretty=""", "--name-only", commit_hash],
                               shell=True, capture_output=True, text=True, encoding="UTF-8").stdout
    return file_name


def get_commit_info(git_repo: Path):
    commits = get_commits(git_repo)
    for single_commit in commits:
        full_info_of_commit = subprocess.run(["git", "show", single_commit, "--stat"], shell=True, capture_output=True,
                                            encoding="UTF-8").stdout
        author = get_author_from_git_log(full_info_of_commit)
        date = get_date_from_git_log(full_info_of_commit)
        message = get_message_from_git_log(single_commit)
        changed_files = get_file_names_from_git_log(single_commit)

        print(full_info_of_commit)
        print(f"{single_commit}\n{author}\n{date}\n{message}\n{changed_files}\n")

        break


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--git-repository", type=Path, required=True,
                        help="Specify the path to the git repository directory")
    parser.add_argument("-l", "--log-file", default='git_info.log',
                        help="Specify the file name where logs should be kept")
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
    if git_repository != "Given repository is valid":
        sys.exit(1)
    get_commit_info(args.git_repository)
    logger.info(" >>> Done")


if __name__ == "__main__":
    args = parse_args()
    logger = configure_logger(args.log_file)
    main(logger=logger)
