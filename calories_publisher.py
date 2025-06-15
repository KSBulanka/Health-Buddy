import paho.mqtt.client as mqtt
import json
import time
import random

# Set up MQTT broker
broker_address = "broker.hivemq.com"  # Use public proxy
port = 1883
topic = "healthbuddy/calories"

# Set up MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, port)

# Simulated calorie data
def generate_mock_calories():
    return random.randint(500, 2000)

# Release calorie data
try:
    while True:
        calories = generate_mock_calories()
        message = json.dumps({"calories": calories})
        client.publish(topic, message)
        print(f"Published calories: {calories}")
        time.sleep(5)  # Publish once every 5 seconds
except KeyboardInterrupt:
    print("Publisher stopped by user.")
finally:
    client.disconnect()