# ACEMD — AceMacroDeck

> **Keyboards are mainstream. Become The Foot Guy.**

ACEMD turns the pedals on a Logitech G29 racing wheel into customizable keyboard controls. Use your feet to play games, trigger shortcuts, launch apps, or control music.

## Features

- **Pedal-to-key mapping** — map the accelerator, brake, and clutch to keyboard keys.
- **Calibration** — detect pedal axes and movement direction.
- **Two-pedal combos** — assign a key to combinations of two pedals.
- **Double-tap app launcher** — double-tap a pedal to launch its configured application.
- **YouTube Music controls** — play/pause, skip tracks, adjust volume, mute, and attempt shuffle.
- **System tray** — hide ACEMD in the tray and start, stop, restore, or quit it from the tray menu.
- **Live feedback** — view raw controller axes and the current pedal/combo state.

## Requirements

- Windows
- Python 3.13 (the included launcher uses `py -3.13`)
- A compatible controller; the current defaults are configured for a Logitech G29
- The Python packages listed below

Install the dependencies from a terminal:

```powershell
py -3.13 -m pip install pygame pyautogui pynput pystray pillow
```

## Run

1. Connect your G29 and make sure Windows recognizes it.
2. Put `main.py` and `start_acemd.bat` in the same folder.
3. Double-click `start_acemd.bat`.

The included batch file currently expects `main.py` at `%USERPROFILE%\Desktop\ACEMD\main.py`. If your project lives somewhere else, edit that path in the batch file.

You can also launch it directly:

```powershell
py -3.13 main.py
```

## First use

1. Start ACEMD.
2. Click **CALIBRATE**, release all pedals, and follow the prompts for each pedal.
3. Check the displayed axis numbers and key bindings.
4. Click **START** to enable pedal input.
5. Click **STOP** before changing calibration or troubleshooting.

The default bindings and axis numbers are starting points, not guaranteed settings for every wheel or driver. Calibrate your own controller before relying on them.

## Controls and behavior

- Pressing one pedal sends its assigned keyboard key.
- Pressing two pedals at once sends the configured combo key instead of the individual pedal keys.
- Pressing all three pedals suppresses keyboard output.
- Double-tapping a pedal within the configured time window launches its assigned application.
- Closing the window hides ACEMD to the system tray. Use **Quit ACEMD** from the tray menu to fully exit.

YouTube Music shortcuts can depend on browser focus and the current player layout. Media keys may control whichever app Windows currently routes media commands to.

## Troubleshooting

- **Controller not detected:** reconnect the wheel, check Windows controller settings, then restart ACEMD.
- **Pedals activate incorrectly:** use **CALIBRATE** and check the live raw-axis readings.
- **Keys remain held or inputs seem stuck:** click **STOP** or fully quit ACEMD.
- **App launcher does nothing:** use **Browse** to select a valid `.exe` file.
- **Python or package error:** confirm Python 3.13 is installed and install the dependencies above.

## Project status

ACEMD is an experimental personal project. Compatibility and behavior may vary with controller drivers, games, browser versions, and Windows settings. Test bindings in a safe, non-critical environment before using them in a game.

## Safety and fair play

ACEMD is an input-remapping tool. Use it in accordance with each game's rules and terms, and avoid using macros or automation where they provide an unfair advantage or are prohibited.

## License

No license has been specified yet. Until one is added, all rights are reserved by the author by default.
