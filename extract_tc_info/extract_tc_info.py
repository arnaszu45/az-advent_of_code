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


def fetch_test_runs_data() -> dict:  # Should this function have tests? Or it supposed to mocked?
    """Fetches test runs data from a remote server, returning the response JSON data as a formatted string."""

    url = "http://10.208.1.21:12001/test_runs"
    params = {
        "project": "Test Automation",
        "limit": 50000000
    }
    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers, data=json.dumps(params),
                            timeout=5)  # Need timeout exception

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data. URL: {response.url}\nStatus: {response.status_code}\nReason: {response.reason}\n")
        return {}

    return response.json()


def get_latest_submission_time(run_test_data: dict, test_case_file_name: str) -> str:
    """From Run tests data extract the latest execution date of test case"""

    submission_times = []
    if "builds" not in run_test_data:
        logger.error("Key 'builds' does not exists in given data")
        return ""

    for build in run_test_data["builds"]:
        try:
            # Which way is better to call? is it okay to use try inside function? If I use get, I could check if it is empty
            # tests = build.get("properties", {}).get("test_scenario", {}).get("tests", {})
            tests = build["properties"]["test_scenario"]["tests"]
        except KeyError as e:
            logger.error(f"Missing or incorrectly formatted data in 'build' properties - {e}.")
            return ""

        for test in tests:
            if test.get("test_file") != test_case_file_name:
                continue

            submission_time = test.get("submission_time")
            if not submission_time:
                logger.error(f"Missing or incorrectly formatted 'submission_time' in 'tests' properties.")  # Should 'submission_time' and 'tests' be saved as a variables so could be used it logger?
                return ""

            datetime_object = datetime.strptime(submission_time, "%Y_%m_%d_%Hh_%Mm")
            formatted_time = datetime_object.strftime("%Y-%m-%d %H:%M")
            submission_times.append(formatted_time)

    if not submission_times:
        return "NOT executed"  # Majority of tests from TestAutomation is not executed, it supposed to happen or I missing something?

    return max(submission_times)


def write_test_cases_data(test_automation_directory: Path) -> dict:
    all_test_cases_data: dict[str, dict[str, str]] = {}

    test_cases = collect_test_cases_from_directory(test_automation_directory)
    test_runs_data = fetch_test_runs_data()

    for test_case in test_cases:
        test_case_file_name = os.path.basename(test_case)
        last_execution_date = get_latest_submission_time(test_runs_data, test_case_file_name)

        test_case_data = {
            "latest_submission_date": last_execution_date,
            "amount_of_executions": "",  # How this supposed to be counted? Should I count how many times 'test_case_file_name' exists in run tests data? Or there could be another method?
        }

        # Current example of json file
        # "test_T1_test_negative_pressure_slice_init_1_2_3_4.py": {
        #     "latest_submission_date": "2024-04-10 18:15"
        # },

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

    test_cases_data = write_test_cases_data(args.test_automation_directory)

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
