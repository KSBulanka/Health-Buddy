import paho.mqtt.client as mqtt
import json
import time
import random

# MQTT connection information
broker_address = "broker.hivemq.com"
broker_port = 1883
topic = "Sensor/BloodPressure"

# MQTT callback function
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print("Message published.")

# Create MQTT client instance
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker server
client.connect(broker_address, broker_port, 60)

# Main Loop: Continuously publishing blood pressure data
try:
    client.loop_start()
    while True:
        # Generate random blood pressure data (systolic and diastolic pressures)
        systolic = random.randint(90, 140)  # Normal range of systolic blood pressure
        diastolic = random.randint(60, 90)  # Normal range of diastolic pressure
        # Construct JSON message
        message = json.dumps({
            "systolic": systolic,
            "diastolic": diastolic
        })
        # Publish a message to a specified topic
        client.publish(topic, message)
        print(f"Published: {message} to topic {topic}")
        # Publish once every 10 seconds
        time.sleep(10)
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT Broker.")
