from pathlib import Path
import pytest
import training_task as tt

text_with_id = Path('TestAutomation/test_cases/Hydraulics/Connector/'
                    'test_cpu1_testing_of_shunt_interlock_sensors_detailed_functionality.py').read_text()
text_without_id = Path('TestAutomation/procedures/program/cleaning.py').read_text()


def test_search_for_pattern_positive_from_string():
    pattern = 'Polarion ID:'
    expected_result = '4AP2-37766'
    found_id = tt.search_for_id_pattern(text_with_id, pattern)
    assert found_id == expected_result


def test_search_for_pattern_negative_from_path():
    pattern = 'Polarion ID:'
    expected_result = ''
    function = tt.search_for_id_pattern(text_without_id, pattern)
    assert function == expected_result


def test_search_for_pattern_empty_string():
    pattern = 'Polarion ID:'
    empty_string = ''
    expected_result = ''
    function = tt.search_for_id_pattern(empty_string, pattern)
    assert function == expected_result


def test_search_for_pattern_different_pattern():
    pattern = 'delay'
    expected_result = 'import'
    function = tt.search_for_id_pattern(text_with_id, pattern)
    assert function == expected_result


def test_get_function_name():
    pattern = 'Stopping cleaning program'
    expected_result = 'stop_cleaning'
    function = tt.get_function_name(text_without_id.find(pattern), text_without_id)
    assert function == expected_result


def test_get_function_name_same_as_pattern():
    pattern = 'stop_cleaning'
    expected_result = 'stop_cleaning'
    function = tt.get_function_name(text_without_id.find(pattern), text_without_id)
    assert function == expected_result


def test_get_function_name_negative_no_definition_before_pattern():
    pattern = 'check_machine_status'
    expected_results = ''
    function_name = tt.get_function_name(text_without_id.find(pattern), text_without_id)
    assert function_name == expected_results


def test_get_function_name_negative_empty_string():
    pattern = 'check_machine_status'
    string = ''
    expected_results = ''
    function_name = tt.get_function_name(string.find(pattern), string)
    assert function_name == expected_results


def test_all_pattern_usages_positive_amount():
    pattern = 'Polarion ID:'
    amount_of_indexes = 1
    position_of_pattern = [997]
    list_of_indexes = tt.find_all_pattern_usages(text_with_id, pattern)
    assert len(list_of_indexes) == amount_of_indexes
    assert list_of_indexes == position_of_pattern


def test_all_pattern_usages_negative_amount():
    pattern = 'Polarion ID:'
    expected_result = []
    amount_of_indexes = 0
    list_of_indexes = tt.find_all_pattern_usages(text_without_id, pattern)
    assert expected_result == list_of_indexes
    assert len(list_of_indexes) == amount_of_indexes


def test_all_pattern_usages_negative_empty_string():
    pattern = 'Polarion ID:'
    empty_string = ''
    expected_result = []
    amount_of_indexes = 0
    list_of_indexes = tt.find_all_pattern_usages(empty_string, pattern)
    assert expected_result == list_of_indexes
    assert len(list_of_indexes) == amount_of_indexes


# ISTQB !!!
