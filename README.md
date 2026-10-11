# ACEMD - AceMacroDeck

> **Keyboards are mainstream. Become The Foot Guy.**

ACEMD turns the pedals on a Logitech G29 racing wheel into customizable keyboard controls. Use your feet to play games, trigger shortcuts, and launch apps.

## Features

- **Pedal-to-key mapping** — map the accelerator, brake, and clutch to keyboard keys.
- **Calibration** — detect pedal axes and movement direction.
- **Two-pedal combos** — assign a key to combinations of two pedals.
- **Double-tap app launcher** — double-tap a pedal to launch its configured application.
- **System tray** — hide ACEMD in the tray and start, stop, restore, or quit it from the tray menu.
- **Live feedback** — view raw controller axes and the current pedal/combo state.

## Requirements

- Windows 10 or Windows 11
- Python 3.13
- A compatible controller; the current defaults are configured for a Logitech G29
- Internet access for the initial dependency installation

## Setup guide

### 1. Install Python

Install Python 3.13 from [python.org](https://www.python.org/downloads/). Make sure the Python Launcher (`py`) is installed. After installation, open Command Prompt and check:

```bat
py -3.13 --version
```

You should see Python 3.13.x. If Windows says the command was not found, rerun the Python installer and enable the Python Launcher, or reinstall Python 3.13.

### 2. Download ACEMD

Go to the [ACEMD repository](https://github.com/justanIndieDev/AceMD) and click **Code → Download ZIP**, then extract the ZIP to a folder you can find again, such as:

```text
%USERPROFILE%\Desktop\ACEMD
```

Alternatively, use the [latest release](https://github.com/justanIndieDev/AceMD/releases) when one is available.

### 3. Install the dependencies

In the extracted ACEMD folder, double-click **install_dependencies.bat** and wait for it to finish. It installs or updates the Python packages ACEMD needs. Keep the window open until it reports success.

If you prefer using a terminal, open PowerShell in the project folder and run:

```powershell
py -3.13 -m pip install --upgrade pip
py -3.13 -m pip install pygame pyautogui pynput pystray pillow
```

### 4. Connect your controller

Connect your Logitech G29 and confirm Windows detects it. Close other controller utilities if they appear to interfere with input. ACEMD currently uses the first controller detected by Pygame.

### 5. Launch ACEMD

Double-click **start_acemd.bat**. The included launcher expects the script at:

```text
%USERPROFILE%\Desktop\ACEMD\main.py
```

If you extracted the repository somewhere else, open `start_acemd.bat` in Notepad and change that path to your actual `main.py` location. You can also open a terminal in the project folder and run:

```powershell
py -3.13 main.py
```

### 6. Calibrate and test

1. Click **CALIBRATE**.
2. Release all pedals and keep the wheel still, then follow the prompts. Press and hold only the pedal requested by each prompt.
3. Check the live axis readings and make sure each pedal is detected correctly.
4. Review the pedal key bindings and two-pedal combo keys.
5. Click **START** to enable input. Click **STOP** to disable it.
6. To fully exit, right-click the ACEMD tray icon and choose **Quit ACEMD**. Closing the window hides it to the tray.

Test the controls in a text editor or another safe, non-critical app before using them in a game.

## Controls and behavior

- Pressing one pedal sends its assigned keyboard key.
- Pressing two pedals at once sends the configured combo key instead of the individual pedal keys.
- Pressing all three pedals suppresses keyboard output.
- Double-tapping a pedal within the configured time window launches its assigned application.
- Closing the window hides ACEMD to the system tray. Use **Quit ACEMD** from the tray menu to fully exit.

## Troubleshooting

- **Python 3.13 not found:** install Python 3.13 and verify `py -3.13 --version`.
- **Dependency installation fails:** check your internet connection, then run `install_dependencies.bat` again. If needed, open Command Prompt and run the terminal commands above to see the full error.
- **Controller not detected:** reconnect the wheel, check Windows controller settings, then restart ACEMD.
- **Pedals activate incorrectly:** use **CALIBRATE** and check the live raw-axis readings.
- **Keys remain held or inputs seem stuck:** click **STOP** or fully quit ACEMD.
- **App launcher does nothing:** use **Browse** to select a valid `.exe` file.

## Project status

ACEMD is an experimental personal project. Compatibility and behavior may vary with controller drivers, games, browser versions, and Windows settings. The setup scripts install Python dependencies; they do not install Python itself or guarantee compatibility with every controller.

## Safety and fair play

ACEMD is an input-remapping tool. Use it in accordance with each game's rules and terms, and avoid using macros or automation where they provide an unfair advantage or are prohibited.

## License

No license has been specified yet. Until one is added, all rights are reserved by the author by default.
