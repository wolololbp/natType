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

### Linux Mint (no admin privileges)
This app can run without administrator rights. Use a user-space Python and install dependencies in a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you see `bash: .venv/bin/activate: No such file or directory`, the virtual environment was not created. Run the `python -m venv .venv` command first, and confirm the `.venv/` folder exists before activating it.

If the `venv` module is unavailable in your system Python, use a user-space Python distribution (such as pyenv or Miniconda) that includes Tkinter and `venv`, then repeat the steps above.

If Tkinter is missing from the system Python, use a user-space Python distribution (such as pyenv or Miniconda) that includes Tkinter. PyAutoGUI does not require system packages for basic keyboard typing; optional screenshot features may require additional system tools, but they are not used by this app.

## How it works
The app uses `pyautogui` to type into the **currently focused** window. After pressing **Start Typing**, you get a short countdown to switch focus to the target application (e.g., Notepad, Word, browser text field).

> Note: You may need to allow Python to control your keyboard in Windows security settings.
