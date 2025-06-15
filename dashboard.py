import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json
from openai import OpenAI
import os
import time

def get_encouragement(heart_rate, step_count, calories, systolic, diastolic, oxygen, sleep_duration):
    try:
        client = OpenAI(
            api_key="sk-SrN9QwmpjDIsP0JFI350jO2sApVUitBQB4kdIoRrExEjwGUw",
            base_url="https://api.moonshot.cn/v1",
        )

        # 构造用户消息，替换占位符
        user_message = f"Heart rate {heart_rate}, steps {step_count}, calories {calories}, BP {systolic}/{diastolic}, SpO2 {oxygen}, sleep {sleep_duration}."

        # 创建聊天完成请求
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {
                    "role": "system",
                    "content": "You're Nyota, my caring friend. You're gentle and encouraging. Use my health data (heart rate, steps, calories, BP, SpO2, sleep) to give brief, warm feedback. Max 30 characters."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.3,
        )

        # 打印完整返回内容，验证是否包含鼓励信息
        print("API 返回内容:", completion)

        return completion.choices[0].message.content

    except Exception as e:
        print(f"发生错误: {e}")
        return ""

class HealthDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        self.last_api_call_time = 0

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

        # Create interface components
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for health data sections
        health_frame = tk.Frame(self.root, bg="#f0f0f0")
        health_frame.pack(pady=10, fill="x", padx=20)

        self.create_heart_rate_section(health_frame)
        self.create_step_count_section(health_frame)
        self.create_calories_section(health_frame)
        self.create_sleep_duration_section(health_frame)
        self.create_blood_pressure_section(health_frame)
        self.create_blood_oxygen_section(health_frame)

        self.create_encouragement_section()
        self.create_animation_section()

    def create_heart_rate_section(self, parent):
        heart_frame = tk.Frame(parent, bg="#f0f0f0")
        heart_frame.pack(pady=10, fill="x", padx=20)

        heart_label = tk.Label(heart_frame, text="Heart Rate:", font=("Arial", 12), bg="#f0f0f0")
        heart_label.pack(side="left")

        self.heart_value = tk.Label(heart_frame, text="0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.heart_value.pack(side="left", padx=10)

        self.heart_progress = ttk.Progressbar(heart_frame, orient="horizontal", length=200, mode="determinate")
        self.heart_progress.pack(side="right", padx=20)

    def create_step_count_section(self, parent):
        step_frame = tk.Frame(parent, bg="#f0f0f0")
        step_frame.pack(pady=10, fill="x", padx=20)

        step_label = tk.Label(step_frame, text="Step Count:", font=("Arial", 12), bg="#f0f0f0")
        step_label.pack(side="left")

        self.step_value = tk.Label(step_frame, text="0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.step_value.pack(side="left", padx=10)

        self.step_progress = ttk.Progressbar(step_frame, orient="horizontal", length=200, mode="determinate")
        self.step_progress.pack(side="right", padx=20)

    def create_calories_section(self, parent):
        calories_frame = tk.Frame(parent, bg="#f0f0f0")
        calories_frame.pack(pady=10, fill="x", padx=20)

        calories_label = tk.Label(calories_frame, text="Calories:", font=("Arial", 12), bg="#f0f0f0")
        calories_label.pack(side="left")

        self.calories_value = tk.Label(calories_frame, text="0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.calories_value.pack(side="left", padx=10)

        self.calories_progress = ttk.Progressbar(calories_frame, orient="horizontal", length=200, mode="determinate")
        self.calories_progress.pack(side="right", padx=20)

    def create_sleep_duration_section(self, parent):
        sleep_frame = tk.Frame(parent, bg="#f0f0f0")
        sleep_frame.pack(pady=10, fill="x", padx=20)

        sleep_label = tk.Label(sleep_frame, text="Sleep Duration:", font=("Arial", 12), bg="#f0f0f0")
        sleep_label.pack(side="left")

        self.sleep_value = tk.Label(sleep_frame, text="0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.sleep_value.pack(side="left", padx=10)

        self.sleep_progress = ttk.Progressbar(sleep_frame, orient="horizontal", length=200, mode="determinate")
        self.sleep_progress.pack(side="right", padx=20)

    def create_blood_pressure_section(self, parent):
        bp_frame = tk.Frame(parent, bg="#f0f0f0")
        bp_frame.pack(pady=10, fill="x", padx=20)

        bp_label = tk.Label(bp_frame, text="Blood Pressure:", font=("Arial", 12), bg="#f0f0f0")
        bp_label.pack(side="left")

        self.bp_value = tk.Label(bp_frame, text="0/0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.bp_value.pack(side="left", padx=10)

        self.bp_progress = ttk.Progressbar(bp_frame, orient="horizontal", length=200, mode="determinate")
        self.bp_progress.pack(side="right", padx=20)

    def create_blood_oxygen_section(self, parent):
        bo_frame = tk.Frame(parent, bg="#f0f0f0")
        bo_frame.pack(pady=10, fill="x", padx=20)

        bo_label = tk.Label(bo_frame, text="Blood Oxygen:", font=("Arial", 12), bg="#f0f0f0")
        bo_label.pack(side="left")

        self.bo_value = tk.Label(bo_frame, text="0%", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.bo_value.pack(side="left", padx=10)

        self.bo_progress = ttk.Progressbar(bo_frame, orient="horizontal", length=200, mode="determinate")
        self.bo_progress.pack(side="right", padx=20)

    def create_encouragement_section(self):
        # 缩小字体大小
        self.encouragement_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#27ae60", wraplength=760)
        self.encouragement_label.pack(pady=10)

    def create_animation_section(self):
        try:
            self.gif = tk.PhotoImage(file="靓仔雪鸮🕶.gif", format="gif -index 0")
            self.image_label = tk.Label(self.root, image=self.gif, bg="#f0f0f0")
            self.image_label.pack(pady=20)

            self.frame_index = 0
            self.update_animation()
        except tk.TclError:
            print("GIF file not found or cannot be loaded. Please check the file path and name.")

    def update_animation(self):
        try:
            self.frame_index += 1
            self.gif = tk.PhotoImage(file="靓仔雪鸮🕶.gif", format=f"gif -index {self.frame_index}")
            self.image_label.config(image=self.gif)
            self.root.after(100, self.update_animation)
        except tk.TclError:
            self.frame_index = 0
            self.root.after(100, self.update_animation)

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

        if topic == self.topics["heart_rate"]:
            try:
                # 安全转换为整数
                heart_rate = int(float(payload))
                self.update_heart_rate(heart_rate)
            except ValueError:
                print(f"Invalid heart rate payload: {payload}")
        elif topic == self.topics["step_count"]:
            try:
                step_count = int(float(payload))
                self.update_step_count(step_count)
            except ValueError:
                print(f"Invalid step count payload: {payload}")
        elif topic == self.topics["calories"]:
            try:
                calories = int(float(json.loads(payload)["calories"]))
                self.update_calories(calories)
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"Error processing calories payload: {e}")
        elif topic == self.topics["sleep_duration"]:
            try:
                sleep_duration = float(json.loads(payload)["sleep_duration"])
                self.update_sleep_duration(sleep_duration)
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"Error processing sleep duration payload: {e}")
        elif topic == self.topics["blood_pressure"]:
            try:
                data = json.loads(payload)
                systolic = int(float(data["systolic"]))
                diastolic = int(float(data["diastolic"]))
                self.update_blood_pressure(systolic, diastolic)
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"Error processing blood pressure payload: {e}")
        elif topic == self.topics["blood_oxygen"]:
            try:
                data = json.loads(payload)
                oxygen = int(float(data["oxygen"]))
                self.update_blood_oxygen(oxygen)
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"Error processing blood oxygen payload: {e}")

    def update_heart_rate(self, heart_rate):
        self.heart_value.config(text=f"{heart_rate} bpm")
        self.heart_progress["value"] = min(heart_rate / 100 * 100, 100)
        self.show_encouragement()

    def update_step_count(self, step_count):
        self.step_value.config(text=f"{step_count} steps")
        self.step_progress["value"] = min(step_count / 10000 * 100, 100)  # 假设10000步为最大值
        self.show_encouragement()

    def update_calories(self, calories):
        self.calories_value.config(text=f"{calories} kcal")
        self.calories_progress["value"] = min(calories / 3000 * 100, 100)  # 假设3000卡路里为最大值
        self.show_encouragement()

    def update_sleep_duration(self, sleep_duration):
        self.sleep_value.config(text=f"{sleep_duration:.1f} hours")  # 显示一位小数
        self.sleep_progress["value"] = min(sleep_duration / 10 * 100, 100)  # 假设10小时为最大值
        self.show_encouragement()

    def update_blood_pressure(self, systolic, diastolic):
        self.bp_value.config(text=f"{systolic}/{diastolic}")
        # 计算进度条，使用收缩压和舒张压的综合评估
        sys_progress = min(systolic / 180 * 100, 100)  # 180为高血压上限
        dia_progress = min(diastolic / 120 * 100, 100)  # 120为高血压上限
        self.bp_progress["value"] = (sys_progress + dia_progress) / 2
        self.show_encouragement()

    def update_blood_oxygen(self, oxygen):
        self.bo_value.config(text=f"{oxygen}%")
        self.bo_progress["value"] = oxygen  # 血氧直接使用百分比
        self.show_encouragement()

    def show_encouragement(self):
        current_time = time.time()
        if current_time - self.last_api_call_time < 30:  # 30秒内不重复调用
            return
        # 安全获取心率值
        heart_text = self.heart_value.cget("text").split()[0]
        try:
            heart_rate = int(float(heart_text))
        except ValueError:
            print(f"Invalid heart rate value: {heart_text}")
            heart_rate = 0

        # 安全获取步数
        step_text = self.step_value.cget("text").split()[0]
        try:
            step_count = int(float(step_text))
        except ValueError:
            print(f"Invalid step count value: {step_text}")
            step_count = 0

        # 安全获取卡路里
        calories_text = self.calories_value.cget("text").split()[0]
        try:
            calories = int(float(calories_text))
        except ValueError:
            print(f"Invalid calories value: {calories_text}")
            calories = 0

        # 安全获取睡眠时间
        sleep_text = self.sleep_value.cget("text").split()[0]
        try:
            sleep_duration = float(sleep_text)
        except ValueError:
            print(f"Invalid sleep duration value: {sleep_text}")
            sleep_duration = 0

        # 安全获取血压
        bp_text = self.bp_value.cget("text")
        try:
            systolic, diastolic = map(int, bp_text.split("/"))
        except (ValueError, IndexError):
            print(f"Invalid blood pressure value: {bp_text}")
            systolic, diastolic = 0, 0

        # 安全获取血氧
        oxygen_text = self.bo_value.cget("text").rstrip("%")
        try:
            oxygen = int(float(oxygen_text))
        except ValueError:
            print(f"Invalid oxygen value: {oxygen_text}")
            oxygen = 0

        encouragement = get_encouragement(heart_rate, step_count, calories, systolic, diastolic, oxygen, sleep_duration)
        # 打印鼓励信息，验证是否正确获取
        print("鼓励信息:", encouragement)

        # 更新界面
        self.encouragement_label.config(text=encouragement)
        self.root.update_idletasks()  # 强制刷新界面


if __name__ == "__main__":
    root = tk.Tk()
    app = HealthDashboard(root)
    root.mainloop()