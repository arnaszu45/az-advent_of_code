from pathlib import Path
import collect_git_info as cg


def test_is_git_repo():
    git_repo = Path("../../../arnas.zuklija/Downloads/git/")
    result = cg.is_git_repo(git_repo.resolve())
    assert result


def test_is_git_repo_not_dir():
    git_repo = Path("../../../arnas.zuklija/advent_of_code_az/pythonProject/collect_git_info.py")
    result = cg.is_git_repo(git_repo.resolve())
    assert not result


def test_is_git_repo_negative():
    git_repo = Path("../../../arnas.zuklija/Desktop/")
    result = cg.is_git_repo(git_repo.resolve())
    assert not result


def test_get_commits():
    git_repo = Path("../../advent_of_code_az")
    result = cg.get_commits(git_repo)
    assert type(result) is list and len(result) > 40


def test_get_commits_empty_repo():
    git_repo = Path("../empty_repo")
    result = cg.get_commits(git_repo)
    assert result == []


def test_get_commits_not_git_repo():
    git_repo = Path("../../../arnas.zuklija/Downloads/TestAutomation")
    result = cg.get_commits(git_repo)
    assert result == []


def test_get_author_and_date_from_git_log():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-03-26 23:21:18 +0200

    wip: fixing stylish

 pythonProject/collect_git_info.py | 13 +++++++++----
 1 file changed, 9 insertions(+), 4 deletions(-)
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == "arnas.zuklija <arnas.zuklija@qdevtechnologies.com>"
    assert date == "2024-03-26 23:21:18 +0200"


def test_get_author_and_date_from_git_log_empty_author():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: 
Date: 

    wip: fixing stylish

 pythonProject/collect_git_info.py | 13 +++++++++----
 1 file changed, 9 insertions(+), 4 deletions(-)
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == ""
    assert date == ""


def test_get_author_and_date_from_git_log_no_author():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Date:   2024-03-26 23:21:18 +0200

    wip: fixing stylish

 pythonProject/collect_git_info.py | 13 +++++++++----
 1 file changed, 9 insertions(+), 4 deletions(-)
    """
    author, date = cg.get_author_and_date_from_git_log(string)
    assert author == ""
    assert date == ""


def test_get_author_and_date_from_git_log_no_date():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>

    wip: fixing stylish

 pythonProject/collect_git_info.py | 13 +++++++++----
 1 file changed, 9 insertions(+), 4 deletions(-)
    """
    result = cg.get_author_and_date_from_git_log(string)
    assert result == ("", "")


def test_get_insertion_or_deletion_from_git_log():
    string = """
    commit 50c76e327549dd683d5a2af8310433589757725f
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 14:57:17 +0200

    Committing not completely done advent of code part 2
    wip: getting rid of necessary subprocess commands

 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
  1 file changed, 9 insertions(+), 4 deletions(-)"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 9
    expected_deletions = 4
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_insertion_or_deletion_from_git_log_no_deletions():
    string = """
    commit 50c76e327549dd683d5a2af8310433589757725f
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 14:57:17 +0200

    Committing not completely done advent of code part 2
    wip: getting rid of necessary subprocess commands

 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 25
    expected_deletions = 0
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_insertion_or_deletion_from_git_log_ones():
    string = """
    commit e78c1fe49557fb8c713790f750b710c740bfb626
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 15:03:24 +0200

    Commiting not completely done advent of code part 2

 pythonProject/advent_of_code_2.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 1
    expected_deletions = 1
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_insertion_or_deletion_from_git_log_no_changes():
    string = """
    commit e78c1fe49557fb8c713790f750b710c740bfb626
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 15:03:24 +0200

    Commiting not completely done advent of code part 2
"""
    insertions = cg.get_insertion_or_deletion_from_git_log(string, 'insertion')
    deletions = cg.get_insertion_or_deletion_from_git_log(string, 'deletion')
    expected_insertions = 0
    expected_deletions = 0
    assert insertions == expected_insertions
    assert deletions == expected_deletions


def test_get_changed_and_renamed_files_from_git_log():
    string = """
        Merge remote-tracking branch 'origin/develop' into update_testscript_38280

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py

     .azuredevops/pull_request_template.md                                                                                                                       |    18 +-
    {services/test_cases/core/web => framework/lib/report_engine/validation}/__init__.py                                                                         |     0
    framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite                                                                             |   Bin 0 -> 90112 bytes
     968 files changed, 163570 insertions(+), 86903 deletions(-)
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == ".azuredevops/pull_request_template.md                                                                                                                       |    18 +-"
    assert modified_files == [".azuredevops/pull_request_template.md",
                              "framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite"]
    assert renamed_files == ["{services/test_cases/core/web => framework/lib/report_engine/validation}/__init__.py"]


def test_get_changed_and_renamed_files_from_git_log_no_renamed():
    string = """

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py

     .azuredevops/ => pull_request_template.md                                                                                                                       |    18 +-
    framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite                                                                             |   Bin 0 -> 90112 bytes
     968 files changed, 163570 insertions(+), 86903 deletions(-)
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == ".azuredevops/ => pull_request_template.md                                                                                                                       |    18 +-"
    assert modified_files == [".azuredevops/ => pull_request_template.md",
                              "framework/unittests/integration/polarion/test_db_20211019_121040_positive.sqlite"]
    assert renamed_files == []


def test_get_changed_and_renamed_files_from_git_log_no_files():
    string = """
    Date:   Fri Nov 25 13:12:29 2022 +0200

        Merge remote-tracking branch 'origin/develop' into update_testscript_38280

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py
"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == ""
    assert modified_files == []
    assert renamed_files == []


def test_get_changed_and_renamed_files_from_git_log_variety():
    string = """
    Date:   Fri Nov 25 13:12:29 2022 +0200

        Merge remote-tracking branch 'origin/develop' into update_testscript_38280

        # Conflicts:
        #       test_cases/EBM/HeparinPump/test_T1_test_heparin_pump.py

 services/{test_cases => project_service_tmt}/requirements.txt                                                                      |     0
 services/{test_cases => project_service_tmt}/run.py                                                                                |     34 +-
 services/{test_cases => project_service_tmt}/unittests/common.py                                                                   |     0
 services/{test_cases => project_service_tmt}/unittests/test_case_fields.py                                                         |    13 +-
 services/{test_cases => project_service_tmt}/unittests/test_data/testcases_process_test_cases_data.py                              |     0
 services/{test_cases => project_service_tmt}/unittests/test_extractor.py                                                           |    45 +-

"""
    first_changed_file_line, modified_files, renamed_files = cg.get_changed_and_renamed_files_from_git_log(string)
    assert first_changed_file_line == "services/{test_cases => project_service_tmt}/requirements.txt                                                                       |     0"
    assert modified_files == ["services/{test_cases => project_service_tmt}/run.py",
                              "services/{test_cases => project_service_tmt}/unittests/test_case_fields.py",
                              "services/{test_cases => project_service_tmt}/unittests/test_extractor.py"]
    assert renamed_files == ["services/{test_cases => project_service_tmt}/requirements.txt",
                             "services/{test_cases => project_service_tmt}/unittests/common.py",
                             "services/{test_cases => project_service_tmt}/unittests/test_data/testcases_process_test_cases_data.py"]


if __name__ == "__main__":
    logger = cg.configure_logger("tester_log.log")
