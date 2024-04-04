import re

string = """
    Date:   Fri Nov 25 13:12:29 2022 +0200

        Merge remote-tracking branch 'origin/develop' into update_testscript_38280

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py

 services/{test_cases => project_service_tmt}/requirements.txt                                                                                                                                                    |     0
 services/{test_cases => project_service_tmt}/run.py                                                                                                                                                              |    34 +-
 services/{test_cases => project_service_tmt}/unittests/common.py                                                                                                                                                 |     0
 services/{test_cases => project_service_tmt}/unittests/test_case_fields.py                                                                                                                                       |    13 +-
 services/{test_cases => project_service_tmt}/unittests/test_data/testcases_process_test_cases_data.py                                                                                                            |     0
 services/{test_cases => project_service_tmt}/unittests/test_extractor.py                                                                                                                                         |    45 +-
 test_cases/EBM/BloodPump/{test_E0401_bp_door_sensor_state_monitoring.py => test_bp_door_sensor_state_monitoring.py}                                                                                              |     2 +-
 test_bp_door_sensor_state_monitoring.py                                                                                                                                                                          |     0 
 test_cases/Hydraulics/Cleaning/{test_rpgm_monitoring_of_diasafe_lifetime_no_message_if_mandatory_rinse_required.py => test_rpgm_monitoring_of_diasafe_lifetime_no_message_if_mandatory_rinse_required_part_1.py} |   183 ++++++++++++++++++--------------
 pythonProject/advent_of_code_2.py                                                                                                                                                                                |     2 +-
 {services/test_cases/core/web => framework/unittests/conductivity_calculation}/__init__.py                                                                                                                       |     2 +-
 test_cases/EBM/BloodPump/{test_E0401_bp_door_sensor_state_monitoring.py => test_bp_door_sensor_state_monitoring.py}                                                                                              |    13 +-
 services/{test_cases => project_service_tmt}/run.py                                                                                                                                                              |    13 +-
{services/test_cases/command.py => project_service_tmt/run.py}                                                                                                                                                    |    34 +-
"""


def process_renamed_string(line: str) -> tuple[str, str]:
    """Process the renamed file line, returns full old and new file names"""

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
            renamed_files["new"] = new_file
            renamed_files["old"] = old_file

        # NOTE: "{}", "=>" indicates, that file is renamed, keeping the new file
        elif "{" in line and "=>" in line:
            _, new_file = process_renamed_string(cropped_line)
            modified_files.append(new_file)
        else:
            modified_files.append(cropped_line)

    return first_changed_file, modified_files, renamed_files
