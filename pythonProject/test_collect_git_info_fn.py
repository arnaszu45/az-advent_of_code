from pathlib import Path
import collect_git_info as cg


def test_is_git_repo():
    git_repo = Path("../../advent_of_code_az")
    result = cg.is_git_repo(git_repo.resolve())
    assert result


def test_is_git_repo_negative():
    git_repo = Path("../../../arnas.zuklija/Downloads/TestAutomation")
    result = cg.is_git_repo(git_repo.resolve())
    assert not result


def test_get_commits():
    git_repo = Path("../../advent_of_code_az")
    result = cg.get_commits(git_repo)
    assert type(result) is list and len(result) > 40


def test_get_commits_empty_repo():
    git_repo = Path("../empty_repo")
    result = cg.get_commits(git_repo)
    print(result)


def test_get_commits_not_git_repo():
    git_repo = Path("../../../arnas.zuklija/Downloads/TestAutomation")
    result = cg.get_commits(git_repo)
    print(result)


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
    result = cg.get_author_and_date_from_git_log(string)
    assert result == ("", "")


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


def test_get_file_names_from_git_log():
    string = """
commit abc7659fec568cd0275aca143001a7493b0527ed
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 13:45:32 +0200

    Commint code of advent of code first task

 pythonProject/.idea/.gitignore                     |    3 +
 .../.idea/inspectionProfiles/profiles_settings.xml |    6 +
 pythonProject/.idea/misc.xml                       |    7 +
 pythonProject/.idea/modules.xml                    |    8 +
 pythonProject/.idea/pythonProject.iml              |   10 +
 pythonProject/.idea/vcs.xml                        |    6 +
 pythonProject/advent_of_code_1.py                  |   21 +
 pythonProject/advent_of_code_1_input               | 1000 ++++++++++++++++++++
 8 files changed, 1061 insertions(+)
    """
    result = cg.get_file_names_from_git_log(string)
    expected_result = ["pythonProject/.idea/.gitignore", ".../.idea/inspectionProfiles/profiles_settings.xml",
                       "pythonProject/.idea/misc.xml", "pythonProject/.idea/modules.xml",
                       "pythonProject/.idea/pythonProject.iml", "pythonProject/.idea/vcs.xml",
                       "pythonProject/advent_of_code_1.py", "pythonProject/advent_of_code_1_input"]
    assert result == expected_result


def test_get_file_names_from_git_log_negative():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>

    wip: fixing stylish

 pythonProject  13 +++++++++----
 1 file changed, 9 insertions(+), 4 deletions(-)
    """
    result = cg.get_file_names_from_git_log(string)
    assert not result


def test_get_file_names_from_git_log_negative_no_name():
    string = """
    commit 0b44f202c497c7efb8599567c92b052ee573afc3
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>

    wip: fixing stylish

 | 13 +++++++++----
 1 file changed, 9 insertions(+), 4 deletions(-)
    """
    result = cg.get_file_names_from_git_log(string)
    assert result == [""]


def test_get_file_names_from_git_log_negative_renamed_files():
    string = """
commit 94f31ac4bcecdc66c4bf1ba33028a7460cf11085
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-03-14 13:46:48 +0200

    wip: uppaded handling bad folders errors

 .../{training_task.py => find_pattern_usage.py}    |  0
 .../{training_task2.py => sort_protocols.py}       | 28 +++++++++++++++-------
 2 files changed, 19 insertions(+), 9 deletions(-)
    """
    result = cg.get_file_names_from_git_log(string)
    expected_result = ["find_pattern_usage.py", "sort_protocols.py"]
    assert result == expected_result


def test_get_message_from_git_log():
    string = """
commit 50c76e327549dd683d5a2af8310433589757725f
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 14:57:17 +0200

    Committing not completely done advent of code part 2

 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)
        """
    _, date = cg.get_author_and_date_from_git_log(string)
    result = cg.get_message_from_git_log(string, date)
    expected_result = "Committing not completely done advent of code part 2"
    assert result == expected_result


def test_get_message_from_git_log_multiple_lines():
    string = """
commit 50c76e327549dd683d5a2af8310433589757725f
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 14:57:17 +0200

    Committing not completely done advent of code part 2
    wip: getting rid of necessary subprocess commands

 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)
        """
    _, date = cg.get_author_and_date_from_git_log(string)
    result = cg.get_message_from_git_log(string, date)
    expected_result = ("Committing not completely done advent of code part 2\n    wip: getting rid of necessary "
                       "subprocess commands")
    assert result == expected_result


def test_get_message_from_git_log_no_message():
    string = """
commit 50c76e327549dd683d5a2af8310433589757725f
Author: Arnas Žuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-02-19 14:57:17 +0200


 pythonProject/advent_of_code_2.py | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)
        """
    _, date = cg.get_author_and_date_from_git_log(string)
    result = cg.get_message_from_git_log(string, date)
    expected_result = ""
    assert result == expected_result


def test_get_message_from_git_log_renamed_files():
    string = """
commit 94f31ac4bcecdc66c4bf1ba33028a7460cf11085
Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
Date:   2024-03-14 13:46:48 +0200

    wip: uppaded handling bad folders errors

 .../{training_task.py => find_pattern_usage.py}    |  0
 .../{training_task2.py => sort_protocols.py}       | 28 +++++++++++++++-------
 2 files changed, 19 insertions(+), 9 deletions(-)
        """
    _, date = cg.get_author_and_date_from_git_log(string)
    print(date)
    result = cg.get_message_from_git_log(string, date)
    expected_result = "wip: uppaded handling bad folders errors"
    assert result == expected_result


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


def test_get_renamed_files_from_git_log():
    string = """
    commit 94f31ac4bcecdc66c4bf1ba33028a7460cf11085
    Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
    Date:   2024-03-14 13:46:48 +0200

        wip: uppaded handling bad folders errors

     .../{training_task.py => find_pattern_usage.py}    |  0
     .../{training_task2.py => sort_protocols.py}       | 28 +++++++++++++++-------
     2 files changed, 19 insertions(+), 9 deletions(-)
        """
    result = cg.get_renamed_files_from_git_log(string)
    expected_result = ["training_task.py => find_pattern_usage.py", "training_task2.py => sort_protocols.py"]
    assert result == expected_result


def test_get_renamed_files_from_git_log_negative():
    string = """
        commit e78c1fe49557fb8c713790f750b710c740bfb626
    Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
    Date:   2024-02-19 15:03:24 +0200

        Commiting not completely done advent of code part 2

     pythonProject/advent_of_code_2.py | 2 +-
     1 file changed, 1 insertion(+), 1 deletion(-)
    """
    result = cg.get_renamed_files_from_git_log(string)
    expected_result = []
    assert result == expected_result


def test_get_renamed_file_line():
    string = """
    commit 94f31ac4bcecdc66c4bf1ba33028a7460cf11085
    Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
    Date:   2024-03-14 13:46:48 +0200

        wip: uppaded handling bad folders errors

     .../{training_task.py => find_pattern_usage.py}    |  0
     .../{training_task2.py => sort_protocols.py}       | 28 +++++++++++++++-------
     2 files changed, 19 insertions(+), 9 deletions(-)
            """
    result = cg.get_renamed_file_line(string)
    expected_result = "     .../{training_task.py => find_pattern_usage.py}    |  0"
    assert result == expected_result


def test_get_renamed_file_line_empty_string():
    string = ""
    result = cg.get_renamed_file_line(string)
    expected_result = ""
    assert result == expected_result


def test_get_renamed_file_line_no_renamed_files():
    string = """
        commit e78c1fe49557fb8c713790f750b710c740bfb626
    Author: arnas.zuklija <arnas.zuklija@qdevtechnologies.com>
    Date:   2024-02-19 15:03:24 +0200

        Commiting not completely done advent of code part 2

     pythonProject/advent_of_code_2.py | 2 +-
     1 file changed, 1 insertion(+), 1 deletion(-)
            """
    result = cg.get_renamed_file_line(string)
    expected_result = ""
    assert result == expected_result


if __name__ == "__main__":
    logger = cg.configure_logger("tester_log.log")
