# Penny AI – Budget Breach Detection System

**Penny AI** is a personal finance monitoring prototype built with Python. It reads and simulates SMS debit alerts, tracks monthly expenses, and triggers real-time budget breach notifications — all through a simple, intelligent GUI dashboard.

> 📦 Project Status: Prototype-ready for demo  
> ⚙️ Tech Stack: Python, Tkinter, JSON, pyttsx3

---

## 🔥 What Penny Does

- 🧠 **Reads SMS Alerts** – parses mock debit SMS messages one by one
- 💰 **Tracks Monthly Spending** – sums debit amounts and compares against your set budget
- 🚨 **Sends Budget Breach Alerts** – via pop-up, voice, and alert logs
- 📊 **Displays Transactions** – logs and visualizes all spending activity
- 🔄 **Processes One SMS at a Time** – each click adds one unseen message
- 🧼 **Resets Cleanly on New Budget** – clears old data for a fresh start

---

## 🧠 How It Works

1. User sets a **monthly budget**
2. Clicks “Process New SMS” to simulate a debit alert
3. Penny reads and logs the transaction
4. Penny checks if monthly spending exceeds the budget
5. If breached:
   - Shows alert pop-up
   - Triggers voice warning
   - Logs alert in `alert_log.json`
6. Setting a new budget resets all data: transactions + SMS history

---

## 📁 Project Structure

📦 Penny/
│
├── actual_dashboard.py # GUI (Tkinter-based)

├── sms_reader.py # Reads one SMS per button click

├── notifier.py # Voice + log alert handler
├── auth_manager.py # Handles user login/registration
├── penny.py # Transaction + budget core logic
│
├── data/
│ ├── mock_sms.json # 20 diverse fake SMS messages
│ ├── processed_sms_ids.json # Tracks which SMSes have been processed
│ ├── budget.json # User's monthly budget config
│ ├── alert_log.json # Stores budget breach alerts
│
├── transactions.json # Full transaction history
├── user_db.json # Registered users
├── README.md # You're reading it 



---

## 👥 Team Breakdown

| Team Member     | Contribution |
|------------------|--------------|
| **Adejoh Caleb** | System architect. Built `auth_manager.py`, `main.py`, `notifier.py`, and `penny.py`. Defined the core logic. |
| **Mariam**       | Created `sms_reader.py`, mock SMS data, and budget logic (`mock_sms.json`, `budget.json`) |
| **Strap**        | Built `notifier.py`, handled `alert_log.json`, and mock data flow |
| **Lexi**         | Designed and developed the GUI (`actual_dashboard.py`) |

---

## 📦 Install Requirements

To run locally:

```bash
pip install pyttsx3
pip install pypiwin32  # for voice alerts on Windows

⚠️ Disclaimer
This is a prototype app built for a live demo/presentation. It does not read real SMS and should not be used for live banking. All data is simulated using JSON.
