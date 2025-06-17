#!/usr/bin/python3
import sys
import json
import time
import configparser
import logging
import xml.etree.cElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from socket import timeout

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

# Load config
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

# Read from config
config = load_config('config.ini')
sensors = [int(x) for x in config['Sensors']['ids'].split(',')]
prtg_settings = config['PRTG']['url']

# Initialize last_recorded dict
last_recorded = {sensor: time.time() - 30 for sensor in sensors}

# Create XML payload for GET request
def prtg_payload(temperature, humidity):
    root = ET.Element("prtg")
    for channel, value in [("Temperature", temperature), ("Humidity", humidity)]:
        result = ET.SubElement(root, "result")
        ET.SubElement(result, "channel").text = channel
        ET.SubElement(result, "value").text = str(value)
        ET.SubElement(result, "float").text = str(1)
    return ET.tostring(root, encoding='unicode')

# Send data to PRTG server with retries
def send_data(sensor_id, temperature, humidity):
    url = f"{prtg_settings}/{sensor_id}?content={prtg_payload(temperature, humidity)}"
    retries = 15
    for attempt in range(retries):
        try:
            contents = urlopen(url, timeout=10)
            logging.info(f'Sent: {url}')
            # Everything went well!
            return
        except HTTPError as e:
            # Handle HTTP errors
            logging.error(f'HTTP Error for sensor {sensor_id}: {e.code} - {e.reason}')
            break
        except URLError as e:
            # URL/Network errors
            logging.error(f'Network Error: {e.reason}')
        except timeout:
            # Most common method of failure - PRTG down for update, network restarted etc.
            logging.error('Network Error: Request timed out')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {str(e)}')
        
        # Exponential backoff
        wait_time = 2 ** attempt
        logging.info(f'Retrying in {wait_time} seconds...')
        time.sleep(wait_time)

for line in sys.stdin:
    decoded = json.loads(line)
    if 'id' not in decoded or 'temperature_F' not in decoded or 'humidity' not in decoded:
        continue
    sensor_id = decoded['id']
    if sensor_id in sensors:
        temperature = decoded['temperature_F']
        humidity = decoded['humidity']
        if time.time() - last_recorded[sensor_id] > 30:
            last_recorded[sensor_id] = time.time()
            logging.info(f'Received data for sensor {sensor_id}: Temp={temperature}, Humidity={humidity}')
            send_data(sensor_id, temperature, humidity)