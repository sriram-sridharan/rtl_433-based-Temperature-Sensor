import sys
import os
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import temp_simplified


def test_payload_structure():
    # Check that the root tag is <prtg> and contains exactly 2 <result> children nodes (temperature and humidity)
    xml_str = temp_simplified.prtg_payload(72.5, 45.0)
    root = ET.fromstring(xml_str)
    assert root.tag == 'prtg'
    results = root.findall('result')
    assert len(results) == 2


def test_payload_temperature_channel():
    # Check that the temperature channel exists, has the correct value, and float=1 (required by PRTG for decimals)
    xml_str = temp_simplified.prtg_payload(72.5, 45.0)
    root = ET.fromstring(xml_str)
    channels = {r.find('channel').text: r for r in root.findall('result')}
    assert 'Temperature' in channels
    assert channels['Temperature'].find('value').text == '72.5'
    assert channels['Temperature'].find('float').text == '1'


def test_payload_humidity_channel():
    # Check that the humidity channel exists, has the correct value, and float=1 (required by PRTG for decimals)
    xml_str = temp_simplified.prtg_payload(72.5, 45.0)
    root = ET.fromstring(xml_str)
    channels = {r.find('channel').text: r for r in root.findall('result')}
    assert 'Humidity' in channels
    assert channels['Humidity'].find('value').text == '45.0'
    assert channels['Humidity'].find('float').text == '1'


def test_payload_negative_temperature():
    # Check that negative temperatures also work
    xml_str = temp_simplified.prtg_payload(-5.0, 80.0)
    root = ET.fromstring(xml_str)
    channels = {r.find('channel').text: r for r in root.findall('result')}
    assert channels['Temperature'].find('value').text == '-5.0'
