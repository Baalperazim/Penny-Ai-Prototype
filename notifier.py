# notifier.py
import json
import os
import pyttsx3

class Notifier:
    def __init__(self, alert_file='data/alert_log.json'):
        self.alert_file = alert_file
        self.voice = pyttsx3.init()

        # Make sure alert log file exists
        if not os.path.exists(self.alert_file):
            with open(self.alert_file, 'w') as f:
                json.dump([], f)

    def send_alert(self, message):
        print(f"[ALERT] {message}")
        self.log_alert(message)
        self.voice_alert(message)

    def log_alert(self, message):
        with open(self.alert_file, 'r') as f:
            alerts = json.load(f)
        alerts.append({"message": message})
        with open(self.alert_file, 'w') as f:
            json.dump(alerts, f, indent=4)

    def voice_alert(self, message):
        self.voice.say(message)
        self.voice.runAndWait()
