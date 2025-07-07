import paho.mqtt.client as mqtt
import random
import time

# Set up MQTT broker
broker_address = "broker.hivemq.com"  # Use public proxy
port = 1883
topic = "healthbuddy/step_count"

# Set up MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, port)

# Simulated step count data
def generate_mock_step_count():
    return random.randint(0, 1000)

# Release step count data
try:
    while True:
        step_count = generate_mock_step_count()
        client.publish(topic, step_count)
        print(f"Published step count: {step_count}")
        time.sleep(5)  # Publish once every 5 seconds
except KeyboardInterrupt:
    print("Publisher stopped by user.")
finally:
    client.disconnect()