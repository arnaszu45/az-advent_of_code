import argparse
import json
import logging
import os.path
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def collect_test_cases_from_directory(test_automation_directory: Path) -> list[Path]:
    """From given TA directory, collects all 'test_*.py' files from '/test_cases/'"""

    if not isinstance(test_automation_directory, Path):
        logger.error(f"{test_automation_directory} - invalid path")
        return []

    test_cases_directory = test_automation_directory / "test_cases"

    if not test_cases_directory.is_dir():
        logger.error(f"{test_cases_directory} - is not a valid directory path")
        return []

    test_cases_files = list(Path(test_cases_directory).rglob("test_*.py"))

    if not test_cases_files:
        logger.warning(f"{test_cases_directory} doesn't have any 'test_*.py' files")
        return []

    return test_cases_files


def fetch_test_runs_data() -> dict:
    """Fetches test runs data from a remote server, returning the response JSON data as a formatted string."""

    url = "http://10.208.1.21:12001/test_runs"
    params = {
        "project": "Test Automation",
        "limit": 5000
    }
    headers = {
        "accept": "application/json"
    }
    response = None

    try:
        response = requests.get(url, params=params, headers=headers, data=json.dumps(params),
                                timeout=5)
    except requests.exceptions.Timeout:
        logger.error(f"The request timed out. Check the access to {url}.")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"No connection - {e}")

    if response is None:
        logger.error(f"Could not get response from {url}")
        return {}

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data. URL: {response.url}\nStatus: {response.status_code}\nReason: {response.reason}\n")
        return {}

    return response.json()


def extract_builds_and_tests(run_test_data: dict, test_case_file_name: str) -> tuple[list, list]:
    """Gets 'builds' and 'tests' from run tests data, which are used in other functions"""

    builds = []
    tests = []

    if "builds" not in run_test_data:
        print("Key 'builds' does not exists in given data")
        return builds, tests

    for build in run_test_data["builds"]:
        try:
            build_tests = build["properties"]["test_scenario"]["tests"]
        except KeyError as e:
            print(f"Missing data in 'build' properties - {e}.")
            return builds, tests

        builds.append(build)

        for test in build_tests:
            if test.get("test_file") == test_case_file_name:
                tests.append(test)

    return builds, tests


def get_latest_submission_time(tests: list) -> str:
    """From Run tests data extract the latest execution date of test case"""

    submission_times = []

    for test in tests:
        submission_time = test.get("submission_time")
        if submission_time:
            try:
                datetime_object = datetime.strptime(submission_time, "%Y_%m_%d_%Hh_%Mm")
                submission_times.append(datetime_object)
            except ValueError:
                print(f"Invalid submission time format: {submission_time}")

    if not submission_times:
        return "NOT executed"

    latest_date = max(submission_times)

    return str(latest_date)


def count_amount_of_executions(test_case_file_name: str, builds: list) -> tuple[int, int]:
    """Count the number of executions for the given test case"""

    failed = 0
    passed = 0

    for build in builds:
        tests = build["properties"]["test_scenario"]["tests"]

        for test in tests:
            if test.get("test_file") != test_case_file_name:
                continue

            if build["results"] == 2:
                failed += 1

            if build["results"] == 0:
                passed += 1

    return passed, failed


def collect_revisions(test_case_file_name: str, builds: list) -> list[str]:
    """From Run tests data takes all the revisions of specific test case"""

    revisions = []

    for build in builds:
        properties = build["properties"]
        tests = build["properties"]["test_scenario"]["tests"]

        for test in tests:
            if test.get("test_file") != test_case_file_name:
                continue
            revision = properties["revision"]
            revisions.append(revision)

    return list(set(revisions))


def calculate_pass_ratio(passed: int, failed: int) -> str:

    if passed + failed == 0:
        return "NOT executed"

    pass_ratio = (passed / (failed + passed)) * 100

    return str(pass_ratio) + "%"


def write_test_cases_data(test_automation_directory: Path, test_runs_data: dict) -> dict:
    all_test_cases_data: dict[str, dict[str, str]] = {}

    test_cases = collect_test_cases_from_directory(test_automation_directory)

    for test_case in test_cases:

        test_case_file_name = os.path.basename(test_case)

        builds, tests = extract_builds_and_tests(test_runs_data, test_case_file_name)

        passed, failed = count_amount_of_executions(test_case_file_name, builds)

        test_case_data = {
            "latest_submission_date": get_latest_submission_time(tests),
            "amount_of_executions": passed + failed,
            "revisions": collect_revisions(test_case_file_name, builds),
            "pass_ratio": calculate_pass_ratio(passed, failed)
        }

        all_test_cases_data[test_case_file_name] = test_case_data

    return all_test_cases_data


def create_json_file(data, json_file_name):
    with open(json_file_name, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_directory", type=Path, required=True,
                        help="Specify the path to the git repository directory")
    parser.add_argument("-j", "--json_file", type=Path, default="test_cases_info.json",
                        help="Specify the json file name, where json output will be kept")
    parser.add_argument("-l", "--log-file", default='test_cases_info.log',
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


def main(logger_: logging.Logger):
    logger_.info(" >>> Running the script\n")

    test_runs_data = fetch_test_runs_data()
    if not test_runs_data:
        sys.exit(1)

    test_cases_data = write_test_cases_data(args.test_automation_directory, test_runs_data)

    try:
        create_json_file(test_cases_data, args.json_file)
    except Exception as e:
        logger_.error(f"Error occurred trying write {args.json_file}: \n{e}")
        sys.exit(1)

    logger_.info(f" >>> Was generated {args.json_file} file in {os.getcwd()} directory")


if __name__ == "__main__":
    args = parse_args()
    logger = configure_logger(args.log_file)
    start = time.time()
    main(logger_=logger)
    end_time = time.time()
    print(end_time - start)
