import sort_protocols as sp
import xml.etree.ElementTree as Et

# def test_parse_xml_file():
#     string = """
#                     <test-script-reference>&lt;a href="https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/Hydraulics/Pressure/test_tmp_monitoring_alarm_reaction_on_exceeding_the_tmp_limit_value_window_including_power_failure.py" target="_top" class="descriptionLink"&gt;https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/Hydraulics/Pressure/test_tmp_monitoring_alarm_reaction_on_exceeding_the_tmp_limit_value_window_including_power_failure.py&lt;/a&gt;</test-script-reference>
#     """
#     Path = "test_output.xml"
#     root = sp.parse_xml_file(Path)
#     assert root == "ta-tool-export"
#     ### But if my function requires whole path, how to simplify that??


def test_get_full_name_from_http_positive():
    string = """
            <protocol project-id="4008APackage2" id="4AP2-65627">
                <test-script-reference>https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/Hydraulics/ConcentrateSupply/test_limitation_of_bicarbonate_pump_step_cd132_ntc133_bibag.py</test-script-reference>
            </protocol>
        """
    element = Et.fromstring(string)
    result = sp.get_full_name_from_http(element)
    assert result == "https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/Hydraulics/ConcentrateSupply/test_limitation_of_bicarbonate_pump_step_cd132_ntc133_bibag.py"


def test_get_full_name_from_http_href():
    string = """
                <protocol project-id="4008APackage2" id="4AP2-66041">
                <test-script-reference>&lt;a href="https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/EBM/OpticalDetector/test_blood_leak_detection_and_run_up_phase_during_reinfusion.py" target="_top" class="descriptionLink"&gt;https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/EBM/OpticalDetector/test_blood_leak_detection_and_run_up_phase_during_reinfusion.py&lt;/a&gt; </test-script-reference>
            </protocol>
    """
    element = Et.fromstring(string)
    result = sp.get_full_name_from_http(element)
    assert result == "https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/EBM/OpticalDetector/test_blood_leak_detection_and_run_up_phase_during_reinfusion.py"


def test_get_full_name_from_http_negative():
    string = """
                <protocol project-id="4008APackage2" id="4AP2-66041">
            </protocol>
    """
    element = Et.fromstring(string)
    result = sp.get_full_name_from_http(element)
    assert result == ""


def test_get_full_name_from_http_negative_bad_protocol():
    string = """
            <protocol project-id="4008APackage2" id="4AP2-68074">
            <test-script-reference>&lt;a href="https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/EBM/Pressure/test_venous_pressure_monitoring_limit_spreading_when_blood_flow_is_reduced_or_increased.py" target="_top" class="descriptionLink"&gt;https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/EBM/Pressure/test_venous_pressure_monitoring_limit_spreading_when_blood_flow_is_reduced_or_increased.py&lt;/a&gt; &lt;span style="color: #000000;"&gt;&lt;br/&gt;
            &lt;/span&gt;</test-script-reference>
    """
    element = Et.fromstring(string)
    result = sp.get_full_name_from_http(element)
    assert result == "https://central.svn.alm.gpdm.fresenius.com/svn/4008A/apps/trunk/test_automation/test_cases/EBM/Pressure/test_venous_pressure_monitoring_limit_spreading_when_blood_flow_is_reduced_or_increased.py"


def test_get_full_name_from_http_br():
    string = """
                <protocol project-id="4008APackage2" id="4AP2-62413">
                <test-script-reference>http://desw-svn1.schweinfurt.germany.fresenius.de/svn/4008A/apps/trunk/test_automation/test_cases/Hydraulics/Cleaning/test_power_recurrence_without_battery_cleaning_program_start_conditions.py&lt;br/&gt;</test-script-reference>
            </protocol>
            """
    element = Et.fromstring(string)
    result = sp.get_full_name_from_http(element)
    assert result == "http://desw-svn1.schweinfurt.germany.fresenius.de/svn/4008A/apps/trunk/test_automation/test_cases/Hydraulics/Cleaning/test_power_recurrence_without_battery_cleaning_program_start_conditions.py"
