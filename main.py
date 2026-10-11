import os
import time
import threading
import pygame
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pynput.keyboard import Controller, Key
import pystray
from PIL import Image, ImageDraw

APP_NAME = "ACEMD — AceMacroDeck"
POLL_MS = 20
PRESS_THRESHOLD = 0.5
DOUBLE_TAP_MS = 400

PEDALS = {
    "Accelerator": {"axis": 1, "key": "insert", "baseline": None, "direction": -1},
    "Brake": {"axis": 2, "key": "down", "baseline": None, "direction": -1},
    "Clutch": {"axis": 3, "key": "space", "baseline": None, "direction": -1},
}

COMBOS = {
    ("Accelerator", "Brake"): {"name": "Accelerator + Brake", "key": "d"},
    ("Accelerator", "Clutch"): {"name": "Accelerator + Clutch", "key": "6"},
    ("Brake", "Clutch"): {"name": "Brake + Clutch", "key": "a"},
}

DEFAULT_APPS = {
    "Accelerator": r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
    "Brake": "",
    "Clutch": "",
}

keyboard = Controller()
root = tk.Tk()
root.title(APP_NAME)
root.geometry("800x900")
root.minsize(650, 600)

running = False
closing = False
joystick = None
tray_icon = None
held_keys = set()
previous_pressed = set()
last_tap = {name: None for name in PEDALS}
app_vars = {}
pedal_key_vars = {}
pedal_axis_vars = {}
pedal_status = {}
combo_key_vars = {}

status_var = tk.StringVar(value="Stopped")
controller_var = tk.StringVar(value="Controller not connected")
combo_var = tk.StringVar(value="No active combo")
raw_var = tk.StringVar(value="Raw axes: —")
delay_var = tk.StringVar(value=str(DOUBLE_TAP_MS))

style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)

top = ttk.Frame(root, padding=12)
top.pack(fill="x")

ttk.Label(top, text="ACEMD", style="Title.TLabel").pack(side="left")
ttk.Label(top, textvariable=status_var).pack(side="right")

controls = ttk.Frame(root, padding=(12, 0, 12, 10))
controls.pack(fill="x")

start_button = ttk.Button(controls, text="START", style="Action.TButton")
stop_button = ttk.Button(controls, text="STOP", style="Action.TButton")
calibrate_button = ttk.Button(controls, text="CALIBRATE", style="Action.TButton")

start_button.pack(side="left", padx=(0, 8))
stop_button.pack(side="left", padx=(0, 8))
calibrate_button.pack(side="left")

ttk.Label(
    root,
    textvariable=controller_var,
    padding=(12, 0, 12, 8),
).pack(anchor="w")

canvas_frame = ttk.Frame(root)
canvas_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

canvas = tk.Canvas(canvas_frame, highlightthickness=0)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
content = ttk.Frame(canvas, padding=8)

content_window = canvas.create_window((0, 0), window=content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfigure(content_window, width=canvas.winfo_width())


content.bind("<Configure>", update_scroll_region)
canvas.bind("<Configure>", update_scroll_region)

ttk.Label(content, text="Pedal bindings", style="Section.TLabel").pack(
    anchor="w", pady=(0, 8)
)

pedal_frame = ttk.Frame(content)
pedal_frame.pack(fill="x")

for name, config in PEDALS.items():
    row = ttk.Frame(pedal_frame, padding=(0, 5))
    row.pack(fill="x")

    ttk.Label(row, text=name, width=14).pack(side="left")

    axis_var = tk.StringVar(value=str(config["axis"]))
    pedal_axis_vars[name] = axis_var

    ttk.Label(row, text="Axis").pack(side="left", padx=(0, 4))
    ttk.Entry(row, textvariable=axis_var, width=4).pack(
        side="left", padx=(0, 10)
    )

    key_var = tk.StringVar(value=config["key"])
    pedal_key_vars[name] = key_var

    ttk.Label(row, text="Key").pack(side="left", padx=(0, 4))
    ttk.Entry(row, textvariable=key_var, width=12).pack(
        side="left", padx=(0, 10)
    )

    state_label = ttk.Label(row, text="Released", width=12)
    state_label.pack(side="right")
    pedal_status[name] = state_label

ttk.Separator(content).pack(fill="x", pady=12)

ttk.Label(content, text="Application launcher", style="Section.TLabel").pack(
    anchor="w", pady=(0, 4)
)

ttk.Label(
    content,
    text="Double-tap a pedal to launch its assigned application.",
    wraplength=680,
).pack(anchor="w", pady=(0, 8))


def browse_app(name):
    path = filedialog.askopenfilename(
        title=f"Select application for {name} double-tap",
        filetypes=[("Applications", "*.exe"), ("All files", "*.*")],
    )
    if path:
        app_vars[name].set(path)


for name in PEDALS:
    row = ttk.Frame(content, padding=(0, 5))
    row.pack(fill="x")

    ttk.Label(row, text=f"{name} × 2", width=18).pack(side="left")

    app_var = tk.StringVar(value=DEFAULT_APPS[name])
    app_vars[name] = app_var

    ttk.Entry(row, textvariable=app_var).pack(
        side="left", fill="x", expand=True, padx=(0, 6)
    )

    ttk.Button(
        row,
        text="Browse",
        command=lambda n=name: browse_app(n),
    ).pack(side="right")

delay_row = ttk.Frame(content, padding=(0, 8))
delay_row.pack(fill="x")

ttk.Label(delay_row, text="Double-tap window (ms)").pack(side="left")
ttk.Entry(delay_row, textvariable=delay_var, width=8).pack(
    side="left", padx=8
)
ttk.Label(delay_row, text="Recommended: 300–500 ms").pack(side="left")

ttk.Separator(content).pack(fill="x", pady=12)

ttk.Label(content, text="Two-pedal combos", style="Section.TLabel").pack(
    anchor="w", pady=(0, 8)
)

ttk.Label(
    content,
    text="Combos override the individual pedal keys while active.",
    wraplength=680,
).pack(anchor="w", pady=(0, 8))

combo_frame = ttk.Frame(content)
combo_frame.pack(fill="x")

for pair, config in COMBOS.items():
    row = ttk.Frame(combo_frame, padding=(0, 5))
    row.pack(fill="x")

    ttk.Label(row, text=config["name"], width=30).pack(side="left")
    ttk.Label(row, text="Key").pack(side="left", padx=(0, 6))

    key_var = tk.StringVar(value=config["key"])
    combo_key_vars[pair] = key_var
    ttk.Entry(row, textvariable=key_var, width=12).pack(side="left")

ttk.Separator(content).pack(fill="x", pady=12)

ttk.Label(content, text="Live controller", style="Section.TLabel").pack(
    anchor="w", pady=(0, 8)
)

ttk.Label(content, textvariable=raw_var, wraplength=680).pack(
    anchor="w", pady=(0, 8)
)

ttk.Label(content, textvariable=combo_var, wraplength=680).pack(
    anchor="w", pady=(0, 8)
)


def parse_key(value):
    value = value.strip().lower()

    if not value:
        raise ValueError("A key binding cannot be empty.")

    aliases = {
        "return": "enter",
        "control": "ctrl",
        "pageup": "page_up",
        "pagedown": "page_down",
        "pgup": "page_up",
        "pgdn": "page_down",
        "del": "delete",
        "ins": "insert",
    }

    value = aliases.get(value, value)

    if len(value) == 1:
        return value

    try:
        return getattr(Key, value)
    except AttributeError:
        raise ValueError(f"Unknown key: {value}")


def release_all_keys():
    global held_keys

    for key in list(held_keys):
        try:
            keyboard.release(key)
        except Exception:
            pass

    held_keys.clear()


def stop_engine():
    global running, previous_pressed

    running = False
    release_all_keys()
    previous_pressed.clear()

    for name in PEDALS:
        last_tap[name] = None
        pedal_status[name].configure(text="Released")

    status_var.set("Stopped")
    combo_var.set("No active combo")


def read_settings():
    for name in PEDALS:
        try:
            axis = int(pedal_axis_vars[name].get())
            if axis < 0:
                raise ValueError

            PEDALS[name]["axis"] = axis
            PEDALS[name]["key"] = pedal_key_vars[name].get().strip()
            parse_key(PEDALS[name]["key"])
        except ValueError:
            raise ValueError(f"Check the axis number and key for {name}.")

    for pair in COMBOS:
        COMBOS[pair]["key"] = combo_key_vars[pair].get().strip()
        parse_key(COMBOS[pair]["key"])

    try:
        delay = int(delay_var.get())
        if not 100 <= delay <= 1500:
            raise ValueError
    except ValueError:
        raise ValueError("The double-tap window must be between 100 and 1500 ms.")

    return delay / 1000


def connect_controller():
    global joystick

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        joystick = None
        controller_var.set("No G29 detected. Connect it and try again.")
        return False

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    controller_var.set(
        f"Connected: {joystick.get_name()} | Axes: {joystick.get_numaxes()}"
    )
    return True


def get_axis_values():
    if joystick is None:
        return []

    pygame.event.pump()
    return [
        joystick.get_axis(i)
        for i in range(joystick.get_numaxes())
    ]


def launch_app(name):
    path = os.path.expandvars(app_vars[name].get().strip())

    if not path:
        status_var.set(f"{name} double-tap: no app configured")
        return

    if not os.path.exists(path):
        status_var.set(f"App path not found for {name}")
        return

    try:
        os.startfile(path)
        status_var.set(f"Launched app for {name}")
    except Exception as error:
        status_var.set(f"Could not launch {name}: {error}")


def set_pressed_keys(desired_keys):
    global held_keys

    for key in held_keys - desired_keys:
        keyboard.release(key)

    for key in desired_keys - held_keys:
        keyboard.press(key)

    held_keys = set(desired_keys)


def start_engine():
    global running, previous_pressed

    if running or closing:
        return

    try:
        double_tap_window = read_settings()
    except ValueError as error:
        messagebox.showerror("Invalid settings", str(error))
        return

    if not connect_controller():
        messagebox.showwarning("Controller missing", controller_var.get())
        return

    values = get_axis_values()

    for name, config in PEDALS.items():
        axis = config["axis"]

        if axis >= len(values):
            messagebox.showerror(
                "Invalid axis",
                f"{name} uses axis {axis}, but the controller has "
                f"{len(values)} axes.",
            )
            return

        config["baseline"] = values[axis]
        last_tap[name] = None

    previous_pressed.clear()
    running = True
    status_var.set("Running")
    poll_controller(double_tap_window)


def poll_controller(double_tap_window):
    global previous_pressed

    if not running or closing:
        return

    try:
        values = get_axis_values()
    except Exception:
        stop_engine()
        controller_var.set("Controller disconnected.")
        return

    if not values:
        stop_engine()
        controller_var.set("Controller unavailable.")
        return

    pressed_pedals = set()

    for name, config in PEDALS.items():
        axis = config["axis"]

        if axis >= len(values):
            stop_engine()
            controller_var.set(f"Axis {axis} is unavailable.")
            return

        value = values[axis]
        baseline = config["baseline"]
        direction = config["direction"]
        is_pressed = (value - baseline) * direction > PRESS_THRESHOLD

        if is_pressed:
            pressed_pedals.add(name)

        pedal_status[name].configure(
            text="PRESSED" if is_pressed else "Released"
        )

    now = time.monotonic()
    newly_pressed = pressed_pedals - previous_pressed

    for name in newly_pressed:
        if len(pressed_pedals) != 1:
            last_tap[name] = None
            continue

        previous_tap = last_tap[name]

        if previous_tap is not None and now - previous_tap <= double_tap_window:
            last_tap[name] = None
            launch_app(name)
        else:
            last_tap[name] = now

    desired_keys = set()
    active_combo = None

    if len(pressed_pedals) == 1:
        name = next(iter(pressed_pedals))
        desired_keys.add(parse_key(PEDALS[name]["key"]))

    elif len(pressed_pedals) == 2:
        pair = tuple(name for name in PEDALS if name in pressed_pedals)

        if pair in COMBOS:
            desired_keys.add(parse_key(COMBOS[pair]["key"]))
            active_combo = COMBOS[pair]["name"]

    set_pressed_keys(desired_keys)

    if active_combo:
        combo_var.set(f"Active combo: {active_combo}")
    elif len(pressed_pedals) == 3:
        combo_var.set("All three pedals pressed — outputs suppressed")
    else:
        combo_var.set("No active combo")

    raw_var.set(
        "Raw axes: " + " | ".join(
            f"{i}: {value:+.2f}" for i, value in enumerate(values)
        )
    )

    previous_pressed = set(pressed_pedals)
    root.after(POLL_MS, lambda: poll_controller(double_tap_window))


def sample_axes(duration=0.7):
    samples = []
    end_time = time.monotonic() + duration

    while time.monotonic() < end_time:
        samples.append(get_axis_values())
        root.update()
        time.sleep(0.02)

    if not samples:
        raise RuntimeError("No controller readings received.")

    axis_count = min(len(sample) for sample in samples)

    return [
        sum(sample[i] for sample in samples) / len(samples)
        for i in range(axis_count)
    ]


def calibrate():
    if running:
        messagebox.showinfo("Stop first", "Press STOP before calibrating.")
        return

    if not connect_controller():
        messagebox.showwarning("Controller missing", controller_var.get())
        return

    try:
        read_settings()
    except ValueError as error:
        messagebox.showerror("Invalid settings", str(error))
        return

    messagebox.showinfo(
        "Calibration",
        "Release every pedal and keep the wheel still. Press OK to sample.",
    )

    try:
        released = sample_axes()
        calibrated_axes = set()

        for name, config in PEDALS.items():
            messagebox.showinfo(
                "Calibration",
                f"Press and hold ONLY the {name.lower()} fully, then press OK.",
            )

            pressed = sample_axes()

            if len(pressed) != len(released):
                raise RuntimeError("The controller axis count changed.")

            differences = [
                abs(pressed[i] - released[i])
                for i in range(len(released))
            ]

            axis = max(range(len(differences)), key=differences.__getitem__)

            if differences[axis] < 0.25:
                messagebox.showwarning(
                    "Calibration issue",
                    f"{name} did not register a clear movement. Try again.",
                )
                return

            if axis in calibrated_axes:
                messagebox.showwarning(
                    "Calibration issue",
                    f"{name} appears to share axis {axis} with another pedal. "
                    "Check the readings and calibrate again.",
                )
                return

            calibrated_axes.add(axis)
            config["axis"] = axis
            config["direction"] = 1 if pressed[axis] > released[axis] else -1
            config["baseline"] = released[axis]
            pedal_axis_vars[name].set(str(axis))

            messagebox.showinfo(
                "Calibration",
                f"{name} calibrated to axis {axis}.",
            )

        messagebox.showinfo(
            "Calibration complete",
            "Release all pedals, then press START.",
        )

    except Exception as error:
        messagebox.showerror("Calibration failed", str(error))


def show_window(icon=None, item=None):
    if not closing:
        root.after(0, restore_window)


def restore_window():
    if closing:
        return

    root.deiconify()
    root.lift()
    root.focus_force()


def hide_window():
    if not closing:
        root.withdraw()


def tray_start(icon, item):
    if not closing:
        root.after(0, start_engine)


def tray_stop(icon, item):
    if not closing:
        root.after(0, stop_engine)


def tray_quit(icon, item):
    if not closing:
        root.after(0, close_app)


def make_tray_image():
    image = Image.new("RGBA", (64, 64), (24, 28, 36, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 3, 61, 61), radius=13, fill=(24, 28, 36, 255))
    draw.rounded_rectangle((8, 8, 56, 56), radius=10, outline=(70, 220, 130, 255), width=3)
    draw.text((17, 15), "A", fill=(70, 220, 130, 255), stroke_width=1)
    return image


def close_app():
    global closing

    if closing:
        return

    closing = True
    stop_engine()

    try:
        if tray_icon is not None:
            tray_icon.stop()
    except Exception:
        pass

    try:
        if joystick is not None:
            joystick.quit()
        pygame.quit()
    except Exception:
        pass

    root.destroy()


def hide_on_close():
    hide_window()


start_button.configure(command=start_engine)
stop_button.configure(command=stop_engine)
calibrate_button.configure(command=calibrate)

root.protocol("WM_DELETE_WINDOW", hide_on_close)

tray_menu = pystray.Menu(
    pystray.MenuItem("Show ACEMD", show_window, default=True),
    pystray.MenuItem("Start controls", tray_start),
    pystray.MenuItem("Stop controls", tray_stop),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Quit ACEMD", tray_quit),
)

tray_icon = pystray.Icon(
    "ACEMD",
    make_tray_image(),
    "ACEMD — AceMacroDeck",
    tray_menu,
)

threading.Thread(target=tray_icon.run, daemon=True).start()
root.mainloop()
