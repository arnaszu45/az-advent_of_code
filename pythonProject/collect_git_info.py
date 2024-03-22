# What has to be done:
# Take git repository
# check if git repos
# Print all commits in given directory
# Collect commits into the list
# for loop through all the commits
# collect all the info from commit
# put that into json file <- commits info
import logging
import argparse
import subprocess
from pathlib import Path
import os
import sys


def check_git_repository(git_repo: Path):
    """Takes directory name and checks if it's Git repository"""

    if not git_repo.is_dir():
        logger.error(f"{git_repo} is not valid directory")
        sys.exit(1)

    with open(os.devnull, "w") as d:
        result = subprocess.run(["git", "-C", str(git_repo), "rev-parse"], stdout=d, stderr=d)
        if result.returncode != 0:
            logger.error(f"Error: {git_repo} is not a git repository.")
            sys.exit(1)


def parse_args():
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
    check_git_repository(args.git_repository)
    logger.info(" >>> Done")


if __name__ == "__main__":
    args = parse_args()
    logger = configure_logger(args.log_file)
    main(logger=logger)