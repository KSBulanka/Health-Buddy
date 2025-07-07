import paho.mqtt.client as mqtt
import json
import time
from flask import Flask, render_template
from openai import OpenAI
import threading

app = Flask(__name__)

dashboard_instance = None  # Global variable to hold the HealthDashboard instance

class HealthDashboard:
    def __init__(self):
        self.heart_rate = 0
        self.step_count = 0
        self.calories = 0
        self.sleep_duration = 0
        self.systolic = 0
        self.diastolic = 0
        self.oxygen = 0
        self.heart_progress = 0
        self.step_progress = 0
        self.last_api_call_time = 0
        self.encouragement = "thinking..."
        self.lock = threading.Lock()  # Create a lock object

        # MQTT settings
        self.broker_address = "broker.hivemq.com"
        self.port = 1883
        self.topics = {
            "heart_rate": "healthbuddy/heart_rate",
            "step_count": "healthbuddy/step_count",
            "calories": "healthbuddy/calories",
            "sleep_duration": "healthbuddy/sleep_duration",
            "blood_pressure": "Sensor/BloodPressure",
            "blood_oxygen": "Sensor/BloodOxygen"
        }

        # Create an MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to an MQTT broker
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            for topic in self.topics.values():
                self.client.subscribe(topic)
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        with self.lock:  # use the lock to protect data access
            if topic == self.topics["heart_rate"]:
                try:
                    self.heart_rate = int(float(payload))
                    self.heart_progress = min(self.heart_rate / 100 * 100, 100)
                except ValueError:
                    print(f"Invalid heart rate payload: {payload}")
            elif topic == self.topics["step_count"]:
                try:
                    self.step_count = int(float(payload))
                    self.step_progress = min(self.step_count / 10000 * 100, 100)
                except ValueError:
                    print(f"Invalid step count payload: {payload}")
            elif topic == self.topics["calories"]:
                try:
                    self.calories = int(float(json.loads(payload)["calories"]))
                    self.calories_progress = min(self.calories / 3000 * 100, 100)
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error processing calories payload: {e}")
            elif topic == self.topics["sleep_duration"]:
                try:
                    self.sleep_duration = float(json.loads(payload)["sleep_duration"])
                    self.sleep_progress = min(self.sleep_duration / 10 * 100, 100)
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error processing sleep duration payload: {e}")
                    # 在 on_message 方法中
            elif topic == self.topics["blood_pressure"]:
                try:
                    data = json.loads(payload)
                    self.systolic = int(float(data["systolic"]))
                    self.diastolic = int(float(data["diastolic"]))
                    bp_progress = (self.systolic / 180 + self.diastolic / 120) / 2 * 100
                    self.bp_progress = min(bp_progress, 100)
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error processing blood pressure payload: {e}")
            elif topic == self.topics["blood_oxygen"]:
                try:
                    data = json.loads(payload)
                    self.oxygen = int(float(data["oxygen"]))
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error processing blood oxygen payload: {e}")

        # call API outside the lock to avoid blocking the MQTT loop
        self.show_encouragement()

    def show_encouragement(self):
        current_time = time.time()
        if current_time - self.last_api_call_time < 30:
            return

        try:
            with self.lock:  # protect data access
                heart_rate = self.heart_rate
                step_count = self.step_count
                calories = self.calories
                sleep_duration = self.sleep_duration
                systolic = self.systolic
                diastolic = self.diastolic
                oxygen = self.oxygen

            # call API to get encouragement
            encouragement = self.get_encouragement(
                heart_rate, step_count, calories,
                systolic, diastolic, oxygen, sleep_duration
            )

            with self.lock:
                self.encouragement = encouragement
                self.last_api_call_time = current_time
        except Exception as e:
            print(f"Error in show_encouragement: {e}")


    def get_encouragement(self, heart_rate, step_count, calories, systolic, diastolic, oxygen, sleep_duration):
        try:
            client = OpenAI(
            api_key="sk-SrN9QwmpjDIsP0JFI350jO2sApVUitBQB4kdIoRrExEjwGUw",
            base_url="https://api.moonshot.cn/v1",
            )

            user_message = (
                f"heartrate: {heart_rate}, step_count: {step_count}, calories: {calories}, "
                f"blood pressure: {systolic}/{diastolic}, blood oxygen: {oxygen}%, sleep duration: {sleep_duration}h。"
            )

            # construct API request
            completion = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {
                        "role": "system",
                        "content": "You're Nyota, my caring friend. You're gentle and encouraging. Use my health data (heart rate, steps, calories, BP, SpO2, sleep) to give brief, warm feedback in English. Max 50 characters."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.3,
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"API calling is wrong: {e}")
            return "Keep living！You're always worth it."

# initialize the dashboard
def create_dashboard():
    global dashboard_instance
    if dashboard_instance is None:
        dashboard_instance = HealthDashboard()
    return dashboard_instance

@app.route('/')
def index():
    dashboard = create_dashboard()
    return render_template('dashboard.html', dashboard=dashboard)

# add a filter to convert timestamp to local time
@app.template_filter('timestamp')
def timestamp_filter(value):
    if value == 0:
        return "NOT YET UPDATED"
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
    except:
        return "TIME FORMAT INCORRECT"

if __name__ == '__main__':
    create_dashboard()  # initialize the mqtt client

    app.run(debug=True, host='0.0.0.0', port=5000)