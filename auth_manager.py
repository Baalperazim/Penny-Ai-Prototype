import random
import string
import json
import os

# Class: AuthManager
class AuthManager:
    def __init__(self, db_file='user_db.json'):
        self.db_file = db_file
        self.users = self.load_users()

    def load_users(self):
        if not os.path.exists(self.db_file):
            return {}
        with open(self.db_file, 'r') as f:
            return json.load(f)

    def save_users(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def generate_otp(self):
        return ''.join(random.choices(string.digits + string.ascii_uppercase, k=6))

    def register_user(self, phone, password):
        if phone in self.users:
            return False, "User already exists."
        self.users[phone] = {"password": password}
        self.save_users()
        return True, "User registered successfully."

    def authenticate_user(self, phone, password):
        return phone in self.users and self.users[phone]['password'] == password