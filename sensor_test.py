#!/usr/bin/env python3

import time 
import board 
import busio 
import logging 
from adafruit_mcp9808 import MCP9808  # Import the MCP9808 library for the temperature sensor 
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient 
import paho.mqtt.client as mqtt # For EC2 Mosquitto
import json 
from threading import Thread

# Configure logging 

logging.basicConfig(level=logging.DEBUG)  # Set the log level to DEBUG for detailed output 
logger = logging.getLogger("AWSIoTPythonSDK.core") 
logger.setLevel(logging.DEBUG)  # Enable debugging for the AWS IoT SDK 

# Initialize I2C bus and temperature sensor(MCP9808) 

i2c_bus = busio.I2C(board.SCL, board.SDA)  # Use the default I2C bus 

sensor = MCP9808(i2c_bus)  # Initialize the MCP9808 sensor for temperature 

# AWS IoT Core settings (replace with actual values) 

host = "a2afgo4w762a5h-ats.iot.us-east-1.amazonaws.com"  # Replace with your actual endpoint  
rootCAPath = "/home/group6/AmazonRootCA1.pem"  # Replace with the Path to your AWS root CA certificate  

# NOTE:(You can download AWS root CA from here: https://www.amazontrust.com/repository/AmazonRootCA1.pem 

certificatePath = "/home/group6/Downloads/RaspberryPi.cert.pem" # Replace with the Path to your device certificate 
privateKeyPath = "/home/group6/Downloads/RaspberryPi.private.key"  # Replace with the path to your device private key 
topic = "raspberrypi/temperature"  # Topic to send temp sensor data 

# EC2 Mosquitto settings

EC2_HOST = "52.1.28.93"  # Replace with your EC2 Elastic IP, e.g., "54.123.456.78"
EC2_PORT = 1883
EC2_TOPIC = "temp/data" # Adjusted topic for temperature data

# MQTT client configuration 

client = AWSIoTMQTTClient("testClient") 
client.configureEndpoint(host, 8883)  # Connect to the AWS IoT endpoint over port 8883 
client.configureCredentials(rootCAPath, privateKeyPath, certificatePath) 

# AWS IoT connection configuration 

client.configureAutoReconnectBackoffTime(1, 32, 20) 
client.configureConnectDisconnectTimeout(10)  # 10 seconds timeout 
client.configureMQTTOperationTimeout(5)  # 5 seconds timeout 

# EC2 Mosquitto MQTT Client

def on_connect_ec2(client, userdata, flags, rc):
    logger.info(f"Connected to EC2 Mosquitto with result code: {rc}")

ec2_client = mqtt.Client()
ec2_client.on_connect = on_connect_ec2
ec2_client.loop_start()

# Function to connect to AWS IoT Core 

def connect_to_aws(): 
    try: 
        client.connect() 
        logger.info("Successfully connected to AWS IoT Core.") 
    except Exception as e: 
        logger.error(f"Error connecting to AWS IoT: {e}") 

# Connect to EC2 Mosquitto
def connect_to_ec2():
    try:
        ec2_client.connect("52.1.28.93", 1883)
        logger.info("Successfully connected to EC2 Mosquitto.")
    except Exception as e:
        logger.error(f"Error connecting to EC2 Mosquitto: {e}")

# Connect to AWS IoT Core 

connect_to_aws() 
connect_to_ec2()
# Infinite loop to continuously read sensor data and publish to AWS IoT 

while True: 

    try: 

# Read temperature from the MCP9808 sensor 

        temperature = sensor.temperature  # Read temperature in Celsius 

# Log the temperature reading 

        logger.info(f"Temperature: {temperature:.2f}C")   

# Prepare the payload to publish to AWS IoT Core 

        payload = json.dumps({ 
            "temperature": str(temperature) 
        }) 

# Publish the temperature data to an MQTT topic 

        client.publish("raspberrypi/temperature", payload, 1) 
        logger.info("Message published to AWS IoT Core.")         

# Publish to EC2 Mosquitto
        ec2_client.publish("temp/data", payload)
        logger.info("Message mirrored to EC2 Mosquitto.")

# Wait for 5 seconds before sending the next reading 

        time.sleep(5) 

    except Exception as e: 

        logger.error(f"Error reading sensor or publishing data: {e}") 
        time.sleep(5)  # Wait for a bit before retrying 

# Simulate DDoS attack (to EC2 only)
def send_ddos():
    while True:
        try:
            for _ in range(50):  # Flood to trigger Suricata "High MQTT Traffic Rate"
                ec2_client.publish(EC2_TOPIC, "DDoS Attack!")
            logger.info("DDoS simulation sent to EC2.")
            time.sleep(0.1)  # Short burst
        except Exception as e:
            logger.error(f"Error in DDoS simulation: {e}")
            time.sleep(5)

# Simulate malformed payload (to EC2 only)
def send_malformed():
    while True:
        try:
            ec2_client.publish(EC2_TOPIC, "{malformed: data")  # Invalid JSON to trigger Suricata
            logger.info("Malformed payload sent to EC2.")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error in malformed payload simulation: {e}")
            time.sleep(5)

# Start connections and threads
if __name__ == "__main__":
    connect_to_aws()
    connect_to_ec2()

    # Run parallel threads
    Thread(target=send_normal_data).start()
    Thread(target=send_ddos).start()
    Thread(target=send_malformed).start()

    # Keep the main thread alive
    while True:
        time.sleep(1)

# Error Debugging for AWS

if not client._mqtt_core._internal_async_client.is_connected():
	logger.error("MQTT client is not connected")

def on_publish(mid):
	print("Publish successful:", mid)

client.on_publish = on_publish

logger.exception("Error reading sensor or publishing data")
