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


def build_scaled_delays(text: str, base_delay: float) -> list[float]:
    delays: list[float] = []
    for char in text:
        if char == "\n":
            delay = base_delay * 1.4
        elif char == "\t":
            delay = base_delay * 1.1
        elif char in ".!?":
            delay = base_delay * 3.2
        elif char in ",;:":
            delay = base_delay * 2.0
        elif char == " ":
            delay = base_delay * 1.6
        else:
            delay = base_delay * 0.55
        delays.append(delay)

    target_total = len(text) * base_delay
    current_total = sum(delays) or 1.0
    scale = target_total / current_total
    return [delay * scale for delay in delays]


def type_human_like(
    text: str,
    wpm: int,
    accuracy: float,
    status_callback,
    pause_event: threading.Event,
) -> None:
    base_delay = seconds_per_char(wpm)
    delays = build_scaled_delays(text, base_delay)
    for idx, char in enumerate(text):
        pause_event.wait()
        if char == "\n":
            pyautogui.press("enter")
            time.sleep(human_delay(delays[idx]))
            continue

        if char == "\t":
            pyautogui.press("tab")
            time.sleep(human_delay(delays[idx]))
            continue

        should_typo = random.random() > accuracy and char.strip() != ""
        if should_typo:
            typo_char = choose_typo_char(char)
            pyautogui.write(typo_char)
            time.sleep(human_delay(delays[idx] * 0.8))
            pyautogui.press("backspace")
            time.sleep(random.uniform(0.05, 0.12))

        pyautogui.write(char)

        time.sleep(human_delay(delays[idx]))

        if idx % 40 == 0 and idx > 0:
            time.sleep(random.uniform(0.1, 0.3))
        status_callback(idx + 1, len(text))


def countdown(seconds: int, status_callback) -> None:
    for remaining in range(seconds, 0, -1):
        status_callback(f"Switch to target window... {remaining}s")
        time.sleep(1)


def run_typing(
    text: str,
    status_callback,
    progress_callback,
    pause_event: threading.Event,
    wpm: int,
) -> None:
    countdown(3, status_callback)
    status_callback("Typing in progress...")
    type_human_like(text, wpm, ACCURACY, progress_callback, pause_event)
    status_callback("Done.")


class App(tk.Tk):
    def __init__(self, title: str = "natType") -> None:
        super().__init__()
        self.title(title)
        self.geometry("720x520")
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.is_running = False

        self.text_input = tk.Text(self, wrap="word", height=16)
        self.text_input.pack(fill="both", expand=True, padx=16, pady=(16, 8))

        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=16)

        self.start_button = ttk.Button(controls, text="Start Typing", command=self.on_start)
        self.start_button.pack(side="left")

        self.pause_button = ttk.Button(
            controls,
            text="Pause",
            command=self.on_pause_toggle,
            state="disabled",
        )
        self.pause_button.pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="Paste text above and click Start Typing.")
        self.status_label = ttk.Label(controls, textvariable=self.status_var)
        self.status_label.pack(side="left", padx=12)

        self.progress_var = tk.StringVar(value="0 / 0")
        self.progress_label = ttk.Label(controls, textvariable=self.progress_var)
        self.progress_label.pack(side="right")

        settings = ttk.Frame(self)
        settings.pack(fill="x", padx=16, pady=(8, 16))

        ttk.Label(settings, text="Speed:").pack(side="left")
        self.speed_var = tk.IntVar(value=WPM)
        self.speed_label = ttk.Label(settings, text=f"{self.speed_var.get()} WPM")
        self.speed_label.pack(side="left", padx=(4, 8))
        self.speed_slider = ttk.Scale(
            settings,
            from_=10,
            to=80,
            orient="horizontal",
            command=self.on_speed_change,
            value=self.speed_var.get(),
        )
        self.speed_slider.pack(side="left", padx=(0, 16), fill="x", expand=True)
        ttk.Label(settings, text="Accuracy:").pack(side="left")
        ttk.Label(settings, text=f"{int(ACCURACY * 100)}%").pack(side="left", padx=(4, 0))

    def on_speed_change(self, value: str) -> None:
        wpm_value = int(float(value))
        self.speed_var.set(wpm_value)
        self.speed_label.configure(text=f"{wpm_value} WPM")

    def on_start(self) -> None:
        text = self.text_input.get("1.0", "end-1c")
        if not text.strip():
            self.status_var.set("Please paste some text first.")
            return

        wpm_value = self.speed_var.get()
        self.is_running = True
        self.pause_event.set()
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal", text="Pause")
        self.progress_var.set(f"0 / {len(text)}")

        def status_callback(message: str) -> None:
            self.status_var.set(message)

        def progress_callback(done: int, total: int) -> None:
            self.progress_var.set(f"{done} / {total}")

        def worker() -> None:
            run_typing(text, status_callback, progress_callback, self.pause_event, wpm_value)
            self.is_running = False
            self.start_button.configure(state="normal")
            self.pause_button.configure(state="disabled", text="Pause")

        threading.Thread(target=worker, daemon=True).start()

    def on_pause_toggle(self) -> None:
        if not self.is_running:
            return
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.status_var.set("Paused. Click Resume to continue.")
            self.pause_button.configure(text="Resume")
        else:
            self.pause_event.set()
            self.status_var.set("Typing in progress...")
            self.pause_button.configure(text="Pause")

if __name__ == "__main__":
    App().mainloop()
