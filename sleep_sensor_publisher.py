import paho.mqtt.client as mqtt
import json
import time
import random

# Set up MQTT broker
broker_address = "broker.hivemq.com"  # Use public proxy
port = 1883
topic = "healthbuddy/sleep_duration"

# Set up MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, port)

# Simulated sleep duration data
def generate_mock_sleep_duration():
    return round(random.uniform(4, 12), 1)

# Release sleep duration data
try:
    while True:
        sleep_duration = generate_mock_sleep_duration()
        message = json.dumps({"sleep_duration": sleep_duration})
        client.publish(topic, message)
        print(f"Published sleep duration: {sleep_duration}")
        time.sleep(5)  # Publish once every 5 seconds
except KeyboardInterrupt:
    print("Publisher stopped by user.")
finally:
    client.disconnect()