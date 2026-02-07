import random
import threading
import time
import tkinter as tk
from tkinter import ttk

import pyautogui

WPM = 33
ACCURACY = 0.98


def seconds_per_char(wpm: int) -> float:
    chars_per_minute = wpm * 5
    return 60 / chars_per_minute


def choose_typo_char(target: str) -> str:
    if target.isalpha():
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        if target.isupper():
            alphabet = alphabet.upper()
        alternatives = [c for c in alphabet if c != target]
        return random.choice(alternatives)
    if target.isdigit():
        digits = [d for d in "0123456789" if d != target]
        return random.choice(digits)
    return random.choice("-_=+;:'\",./?[]{}\\|`~")


def human_delay(base_delay: float) -> float:
    jitter = random.uniform(-0.08, 0.12)
    return max(0.03, base_delay + jitter)


def type_human_like(text: str, wpm: int, accuracy: float, status_callback) -> None:
    base_delay = seconds_per_char(wpm)
    for idx, char in enumerate(text):
        if char == "\n":
            pyautogui.press("enter")
            time.sleep(human_delay(base_delay) + random.uniform(0.05, 0.12))
            continue

        if char == "\t":
            pyautogui.press("tab")
            time.sleep(human_delay(base_delay))
            continue

        should_typo = random.random() > accuracy and char.strip() != ""
        if should_typo:
            typo_char = choose_typo_char(char)
            pyautogui.write(typo_char)
            time.sleep(human_delay(base_delay))
            pyautogui.press("backspace")
            time.sleep(random.uniform(0.05, 0.12))

        pyautogui.write(char)

        delay = human_delay(base_delay)
        if char in ".,;:!?":
            delay += random.uniform(0.05, 0.2)
        if char == " ":
            delay += random.uniform(0.02, 0.1)
        time.sleep(delay)

        if idx % 40 == 0 and idx > 0:
            time.sleep(random.uniform(0.1, 0.3))
        status_callback(idx + 1, len(text))


def countdown(seconds: int, status_callback) -> None:
    for remaining in range(seconds, 0, -1):
        status_callback(f"Switch to target window... {remaining}s")
        time.sleep(1)


def run_typing(text: str, status_callback, progress_callback) -> None:
    countdown(3, status_callback)
    status_callback("Typing in progress...")
    type_human_like(text, WPM, ACCURACY, progress_callback)
    status_callback("Done.")


class App(tk.Tk):
    def __init__(self, title: str = "natType") -> None:
        super().__init__()
        self.title(title)
        self.geometry("720x520")

        self.text_input = tk.Text(self, wrap="word", height=16)
        self.text_input.pack(fill="both", expand=True, padx=16, pady=(16, 8))

        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=16)

        self.start_button = ttk.Button(controls, text="Start Typing", command=self.on_start)
        self.start_button.pack(side="left")

        self.status_var = tk.StringVar(value="Paste text above and click Start Typing.")
        self.status_label = ttk.Label(controls, textvariable=self.status_var)
        self.status_label.pack(side="left", padx=12)

        self.progress_var = tk.StringVar(value="0 / 0")
        self.progress_label = ttk.Label(controls, textvariable=self.progress_var)
        self.progress_label.pack(side="right")

        settings = ttk.Frame(self)
        settings.pack(fill="x", padx=16, pady=(8, 16))

        ttk.Label(settings, text="Fixed speed:").pack(side="left")
        ttk.Label(settings, text=f"{WPM} WPM").pack(side="left", padx=(4, 16))
        ttk.Label(settings, text="Accuracy:").pack(side="left")
        ttk.Label(settings, text=f"{int(ACCURACY * 100)}%").pack(side="left", padx=(4, 0))

    def on_start(self) -> None:
        text = self.text_input.get("1.0", "end-1c")
        if not text.strip():
            self.status_var.set("Please paste some text first.")
            return

        self.start_button.configure(state="disabled")
        self.progress_var.set(f"0 / {len(text)}")

        def status_callback(message: str) -> None:
            self.status_var.set(message)

        def progress_callback(done: int, total: int) -> None:
            self.progress_var.set(f"{done} / {total}")

        def worker() -> None:
            run_typing(text, status_callback, progress_callback)
            self.start_button.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
