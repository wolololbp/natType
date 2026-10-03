# natType

A simple Windows 11 desktop app that accepts a pasted block of text and then types it out using human-like typing patterns at **33 WPM** and **98% accuracy**.

## Features
- Paste text into a textbox and click **Start Typing**.
- Simulated human typing cadence (variable delays, word pauses).
- 98% accuracy simulation (occasional typo + correction).

## Requirements
- Windows 11 or Linux Mint
- Python 3.10+ recommended

## Install
```bash
pip install -r requirements.txt
```

## Run (Windows 11)
```bash
python app.py
```

## Run (Linux Mint)
```bash
python app_linux.py
```

### Linux Mint dependencies
You may need to install system packages for Tkinter and PyAutoGUI:
```bash
sudo apt-get install python3-tk scrot
```

## How it works
The app uses `pyautogui` to type into the **currently focused** window. After pressing **Start Typing**, you get a short countdown to switch focus to the target application (e.g., Notepad, Word, browser text field).

> Note: You may need to allow Python to control your keyboard in Windows security settings.
