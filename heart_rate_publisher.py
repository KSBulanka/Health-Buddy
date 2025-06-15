import paho.mqtt.client as mqtt
import time
import random

# Set the MQTT broker
broker_address = "broker.hivemq.com"  # Use a public broker
port = 1883
topic = "healthbuddy/heart_rate"

# Set up the MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, port)

# Simulate heart rate data
def generate_mock_heart_rate():
    return random.randint(60, 100)

# Publish heart rate data
try:
    while True:
        heart_rate = generate_mock_heart_rate()
        client.publish(topic, heart_rate)
        print(f"Published heart rate: {heart_rate}")
        time.sleep(5)  # Publish every 5 seconds
except KeyboardInterrupt:
    print("Publisher stopped by user.")
finally:
    client.disconnect()