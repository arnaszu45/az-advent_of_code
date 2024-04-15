import argparse
import json
import logging
import os.path
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def collect_test_cases_from_directory(test_automation_directory: Path) -> list[Path]:
    """From given TA directory, collects all 'test_*.py' files from '/test_cases/'"""

    if not isinstance(test_automation_directory, Path):
        logger.error(
            f"'{test_automation_directory}' expected to be Path type, got {type(test_automation_directory)} instead"
        )
        return []

    test_cases_directory = test_automation_directory / "test_cases"

    if not test_cases_directory.is_dir():
        logger.error(f"{test_cases_directory} - is not a directory")
        return []

    test_cases_files = list(Path(test_cases_directory).rglob("test_*.py"))

    if not test_cases_files:
        logger.warning(f"{test_cases_directory} doesn't have any 'test_*.py' files")
        return []

    return test_cases_files


def fetch_test_runs_data(ip_address: str, project_name: str, limit: int) -> dict | None:
    """Fetches test runs data from a remote server, returning the response JSON data as a formatted string."""

    url = f"http://{ip_address}/test_runs"
    params = {
        "project": project_name,
        "limit": limit
    }
    headers = {
        "accept": "application/json"
    }
    try:
        response = requests.get(url, params=params, headers=headers, data=json.dumps(params), timeout=5)
    except Exception as e:
        logger.error(f"The request timed out. Error message:\n{e}.")
        return None

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data. URL: {response.url}\nStatus: {response.status_code}\nReason: {response.reason}\n")
        return None

    return response.json()


def traverse_json(build: dict, keys: list) -> dict | None:
    """Traverse through a nested dictionary using a list of keys and return the value if found, otherwise None."""

    current_data: dict | None = build
    for key in keys:
        current_data = current_data.get(key)

        if current_data is None:
            logger.info(f"Missing key {key!r}")
            return None

    return current_data


def process_the_run_tests_data(run_tests_data: dict) -> dict:
    """Process the test run data and saves the information in easily accessible format"""
    extracted_info = {}

    builds = traverse_json(run_tests_data, keys=["builds"])
    if builds is None:
        return {}

    for build in builds:
        test_scenario = traverse_json(build, keys=["properties", "test_scenario"])

        if test_scenario is None:
            return {}

        tests_info = traverse_json(test_scenario, keys=["tests"])
        if tests_info is None:
            return {}

        for test in tests_info:
            test_file = test.get('test_file', "")
            submission_time = test.get('submission_time', "")
            results = build.get('results', "")
            properties = build.get('properties', {})
            revision = properties.get('revision', "")

            if test_file not in extracted_info:
                extracted_info[test_file] = []
            extracted_info[test_file].append(
                {
                    "submission_time": submission_time,
                    "results": results,
                    "revision": revision
                }
            )

    return extracted_info


def get_latest_submission_time(test_case_info) -> str:
    """From Run tests data extract the latest execution date of test case"""

    if test_case_info is None:
        return ""

    latest_submission = max(test_case_info, key=lambda x: x["submission_time"])
    try:
        latest_submission = datetime.strptime(latest_submission["submission_time"], "%Y_%m_%d_%Hh_%Mm")
    except ValueError:
        logger.info(f"Invalid submission time format: {latest_submission}")

    return str(latest_submission)


def count_amount_of_executions(test_case_info) -> tuple[int, int]:
    """Count the number of executions for the given test case"""

    failed = 0
    passed = 0

    if not test_case_info:
        return 0, 0

    for test_run in test_case_info:
        if test_run["results"] == 0:
            passed += 1
        elif test_run["results"] == 2:
            failed += 1

    return failed, passed


# def collect_revisions(test_case_file_name: str, builds: list) -> list[str]:
#     """From Run tests data takes all the revisions of specific test case"""
#
#     revisions = []
#
#     for build in builds:
#         properties = build["properties"]
#         tests = build["properties"]["test_scenario"]["tests"]
#
#         for test in tests:
#             if test.get("test_file") != test_case_file_name:
#                 continue
#             revision = properties["revision"]
#             revisions.append(revision)
#
#     return list(set(revisions))
#
#
def calculate_pass_ratio(passed: int, failed: int) -> float:
    if passed + failed == 0:
        return 0.0

    pass_ratio = (passed / (failed + passed)) * 100

    return pass_ratio


def write_test_cases_data(test_automation_directory: Path, test_runs_data: dict) -> dict:
    all_test_cases_data: dict[str, dict[str, str]] = {}
    test_cases = collect_test_cases_from_directory(test_automation_directory)

    if not test_cases:
        logger.info(f"Any testcases were found in {test_automation_directory}")
        return {}

    extracted_data = process_the_run_tests_data(test_runs_data)

    if not extracted_data:
        logger.info(f"Tests run data is empty")
        return {}

    for test_case in test_cases:
        test_case_file_name = test_case.name

        test_case_info = extracted_data.get(test_case_file_name)

        failed, passed = count_amount_of_executions(test_case_info)

        test_case_data = {
            "latest_submission_date": get_latest_submission_time(test_case_info),
            "amount_of_executions": passed + failed,
            # "revisions": collect_revisions(test_case_file_name, builds),
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
    parser.add_argument("-log", "--log-file", default='test_cases_info.log',
                        help="Specify the file name, where logs should be kept")
    parser.add_argument("-ip", "--ip_address", type=str, default="10.208.1.21:12001",
                        help="Specify the ip address for url, from where data will be extracted")
    parser.add_argument("-p", "--project_name", type=str, default="Test Automation",
                        help="Specify the project name to get data for")
    parser.add_argument("-l", "--limit", type=int, default=1000,
                        help="Specify the integer value by which to limit the query size")
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

    # TODO: this for using requests
    # test_runs_data = fetch_test_runs_data(ip_address=args.ip_address, project_name=args.project_name,
    #                                       limit=args.limit)
    # if test_runs_data is None:
    #     sys.exit(1)
    #
    # if not test_runs_data:
    #     logger.info("Test runs data is empty.")
    #     return {}

    # # TODO: Delete this for using requests, now data is used from local file
    with open('data_input.json', 'r') as file:
        test_runs_data = json.load(file)

    test_cases_data = write_test_cases_data(args.test_automation_directory, test_runs_data)

    if not test_cases_data:
        sys.exit(1)

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
