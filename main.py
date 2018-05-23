#!/usr/bin/python
import sys
import os
import json
import urllib
import urllib2
import xml.etree.cElementTree as ET
import time

# ***************************** ***************************** #
# ******************* Configuration - edit this ******************* #
# I'm hardcoding sensor IDs to prevent reading other sensors that might be in the area.
sensor1 = 0000
sensor2 = 1111

# PRTG Domain, port and sensor guid/token
# <http or https>://<domain>:<port>
prtg_settings = 'http://myprtg.com:8080'
# sensor guid in PRTG
prtg_token_sensor1 = "0000Token"
prtg_token_sensor2 = "1111Token"

# IFTTT settings (optional)
# IFTTT Webhook Event Name
event_name = "IFTTT%20EVENT"

# IFTTT Webhook token from https://ifttt.com/services/maker_webhooks/settings
ifttt_token = "IFTTTTOKEN"

# rtl_433 arguments See https://github.com/merbanan/rtl_433/blob/master/README.md for flags
rtl_433_arg = ' -q -W -R 40 -F json -C customary -T 20'
# ******************* End config ******************* #
# ************************* ************************* #

# Average Function
def list_avg (passed_array):
	return sum(passed_array)/len(passed_array)

# Create XML payload for GET request
def prtg_payload (temperature, humidity):
	root = ET.Element("prtg")
	result = ET.SubElement(root, "result")
	temp_xml = ET.SubElement(result, "channel")
	temp_xml.text = "Temperature"
	tempval_xml = ET.SubElement(result, "value")
	tempval_xml.text = str(temperature)
	float_xml = ET.SubElement(result, "float")
	float_xml.text = str(1)
	result2 = ET.SubElement(root, "result")
	hum_xml = ET.SubElement(result2, "channel")
	hum_xml.text = "Humidity"
	humval_xml = ET.SubElement(result2, "value")
	humval_xml.text = str(humidity)
	float_xml = ET.SubElement(result2, "float")
	float_xml.text = str(1)
	return ET.tostring(root)


while True:

	# Initialize array here so that error reporting not affected by stale/previously stored values
	# Array for sensor 1
	Array_sensor1 = []
	# Initialize the first to elements of Array_sensor1 to be arrays themselves
	# [0] is temperature, [1] is humidity
	Array_sensor1.append([])
	Array_sensor1.append([])

	# Array for sensor 2
	Array_sensor2 = []
	# Initialize the first to elements of Array_sensor2 to be arrays themselves
	# [0] is temperature, [1] is humidity
	Array_sensor2.append([])
	Array_sensor2.append([])

	# Read the current sensor data and clean
	process = os.popen('rtl_433'+rtl_433_arg)
	rtl_read = process.read()
	process.close()
	rtl_read = rtl_read.strip()
	# SDR tuner is likely unplugged if there's no read data
	if len(rtl_read)==0:
		print >> sys.stderr, "The rtl_sdr tuner does not seem to be operational. Please make sure it is plugged in completely."
		tuner_error_url = "https://maker.ifttt.com/trigger/" + event_name + "/with/key/" + ifttt_token + "?value1=" + "rtl_sdr Tuner"
		# IFTTT error handling start
		try:
			contents = urllib2.urlopen(tuner_error_url).read()
		except urllib2.HTTPError:
			print >> sys.stderr, "Error connecting to IFTTT"
		except urllib2.URLError:
			print >> sys.stderr, "Error connecting to IFTTT"
		# Sleep for longer since this is a hardware issue and requires user intervention
		time.sleep(3600)
		continue
		# IFTTT error handling complete
	rtl_prep = rtl_read.splitlines()
	# Extract data
	for eachline in rtl_prep:
		encoded = json.loads(eachline)
		if encoded["sensor_id"]==sensor1:
			Array_sensor1[0].append(encoded["temperature_F"])
			Array_sensor1[1].append(encoded["humidity"])
		elif encoded["sensor_id"]==sensor2:
			Array_sensor2[0].append(encoded["temperature_F"])
			Array_sensor2[1].append(encoded["humidity"])
	
	# Error handling (out of battery, out of range, etc.) start
	try:
		# Print to console for debugging
		print "Average Sensor 1 Temp is " + str(list_avg(Array_sensor1[0])) + "F"
		print "Average Sensor 1 Humidity is " + str(list_avg(Array_sensor1[1])) + "%"
		print "Average Sensor 2 Temp is " + str(list_avg(Array_sensor2[0])) + "F"
		print "Average Sensor 2 Humidity is " + str(list_avg(Array_sensor2[1])) + "%"
		living_url = prtg_settings + "/" + prtg_token_sensor1 + "?content=" + prtg_payload(list_avg(Array_sensor1[0]), list_avg(Array_sensor1[1]))
		print "Living: " + living_url
		bed_url = prtg_settings + "/" + prtg_token_sensor2 + "?content=" + prtg_payload(list_avg(Array_sensor2[0]), list_avg(Array_sensor2[1]))
		print "Bed: " + bed_url
	except ZeroDivisionError:
		if len(Array_sensor1[0])==0 or len(Array_sensor1[1])==0:
			print >> sys.stderr, "Sensor "+ str(sensor1) + " does not seem to be operational."
			sensor1_error_url = "https://maker.ifttt.com/trigger/" + event_name + "/with/key/" + ifttt_token + "?value1=" + str(sensor1)
			# IFTTT error handling start
			try:
				contents = urllib2.urlopen(sensor1_error_url).read()
			except urllib2.HTTPError:
				print >> sys.stderr, "Error connecting to IFTTT"
			except urllib2.URLError:
				print >> sys.stderr, "Error connecting to IFTTT"
			# IFTTT error handling complete
		elif len(Array_sensor2[0])==0 or len(Array_sensor2[1])==0:
			print >> sys.stderr, "Sensor "+ str(sensor2) + " does not seem to be operational."
			sensor2_error_url = "https://maker.ifttt.com/trigger/" + event_name + "/with/key/" + ifttt_token + "?value1=" + str(sensor2)
			# IFTTT error handling start
			try:
				contents = urllib2.urlopen(sensor2_error_url).read()
			
			except urllib2.HTTPError:
				print >> sys.stderr, "Error connecting to IFTTT"
			except urllib2.URLError:
				print >> sys.stderr, "Error connecting to IFTTT"
			# IFTTT error handling complete
		# If there are errors, no point in proceeding any further
		continue
		# Error handling (out of battery, out of range, etc.) complete
	# PRTG error handling start
	try:
		contents = urllib2.urlopen(living_url)
		contents = urllib2.urlopen(bed_url)
	except urllib2.HTTPError:
		print >> sys.stderr, "Error connecting to PRTG"
	except urllib2.URLError:
		print >> sys.stderr, "Error connecting to PRTG"
	# PRTG error handling complete
	time.sleep(45)