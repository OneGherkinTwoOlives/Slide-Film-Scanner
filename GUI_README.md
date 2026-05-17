# PiSlide Scanner GUI - Setup and Usage Guide

## Overview
The PiSlide Scanner GUI provides a user-friendly graphical interface for the PiSlide automated film slide scanner. It replaces command-line operation with a modern, cross-platform desktop application.

## Key Features
✅ **Cross-platform**: Works on Windows and Linux (Ubuntu)  
✅ **START and E-STOP buttons**: Full control with emergency stop capability  
✅ **Form-based inputs**: No more command-line prompts  
✅ **"Use Last" button**: Recalls previous description  
✅ **"Continue from Last" button**: Auto-increments from last photo number  
✅ **Real-time status**: Live logging and progress tracking  
✅ **Configuration persistence**: Automatically saves your last settings  

---

## Installation

### Prerequisites
- Python 3.7 or higher
- pySerial library
- tkinter (usually included with Python)

### Step 1: Install Python Dependencies
```bash
# Install pySerial
pip install pyserial
```

### Step 2: Verify tkinter is installed
```bash
# Test tkinter
python -m tkinter
```
If a small window appears, tkinter is installed. If not:
- **Windows**: Reinstall Python with "tcl/tk" option checked
- **Linux**: `sudo apt-get install python3-tk`

---

## Quick Start

### Windows
1. **Double-click** `launch_pislide_gui.bat`
   - This will open the GUI automatically

2. **Create Desktop Shortcut** (optional):
   - Right-click `launch_pislide_gui.bat`
   - Select "Create shortcut"
   - Drag the shortcut to your Desktop

### Linux (Ubuntu)
1. **Make launcher executable**:
   ```bash
   chmod +x launch_pislide_gui.sh
   ```

2. **Run the launcher**:
   ```bash
   ./launch_pislide_gui.sh
   ```

3. **Create Desktop Icon** (optional):
   ```bash
   # Edit PiSlide.desktop and replace %INSTALL_DIR% with full path
   nano PiSlide.desktop
   
   # Copy to applications folder
   cp PiSlide.desktop ~/.local/share/applications/
   
   # Make launcher executable
   chmod +x launch_pislide_gui.sh
   ```

---

## Using the GUI

### Main Interface

```
┌─────────────────────────────────────────────────┐
│          PiSlide Film Scanner                   │
├─────────────────────────────────────────────────┤
│  Scan Configuration                             │
│  ┌───────────────────────────────────────────┐  │
│  │ Description:    [____________] [Use Last] │  │
│  │ Last Photo #:   [____] [Continue from Last]│  │
│  │ Number of Cycles: [____]                   │  │
│  │ Serial Port:    [COM6]                     │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│     [START SCAN]      [E-STOP]                  │
│                                                  │
│  Status                                          │
│  ┌───────────────────────────────────────────┐  │
│  │ [10:23:45] Connected successfully!         │  │
│  │ [10:23:46] Homing Y axis...                │  │
│  │ [10:23:50] Y axis homed successfully       │  │
│  │ ...                                         │  │
│  └───────────────────────────────────────────┘  │
│  [████████████████░░░░░░░░░░] 65%              │
│              Cycle 13/20                        │
└─────────────────────────────────────────────────┘
```

### Input Fields

1. **Description**: Batch description (e.g., "Summer 1985, Vermont")
   - Click "Use Last" to load the last description from log file

2. **Last Photo #**: Starting photo number
   - Enter 0 to start fresh
   - Click "Continue from Last" to auto-load last photo number + description

3. **Number of Cycles**: How many scan cycles to perform
   - Each cycle = forward move, pause, backward move, photo capture

4. **Serial Port**: 
   - Windows: Usually `COM6` (check Device Manager)
   - Linux: Usually `/dev/ttyUSB0` or `/dev/ttyACM0`

### Control Buttons

- **START SCAN**: Begin the scanning process
  - Validates all inputs before starting
  - Saves configuration for next time
  
- **E-STOP**: Emergency stop (same as Ctrl-C)
  - Stops motion immediately
  - Attempts graceful disconnect from Marlin
  - Use if something goes wrong

### Status Display

The status area shows:
- Timestamped log messages
- Connection status
- Motion progress
- Photo capture results
- Errors and warnings (color-coded)

Progress bar shows overall completion percentage.

---

## Advanced Features

### Configuration Persistence
Settings are automatically saved to `pislide_config.json`:
- Last description
- Last photo number
- Number of cycles
- Serial port

This file is loaded when the GUI starts.

### Photo Logging
All photos are logged to `log.txt` in the format:
```
Photo #1: Summer 1985, Vermont
Photo #2: Summer 1985, Vermont
Photo #3: Summer 1985, Vermont
```

The "Use Last" and "Continue from Last" buttons read from this log.

### Error Handling
- Invalid inputs trigger friendly error dialogs
- Connection errors are logged with details
- Emergency stop attempts graceful shutdown
- Window close protection during active scans

---

## Troubleshooting

### "Serial port not found"
- **Windows**: Check Device Manager → Ports (COM & LPT)
- **Linux**: Check `ls /dev/ttyUSB* /dev/ttyACM*`
- Verify Arduino/ESP32 is connected and powered
- Try a different USB port or cable

### "Permission denied" (Linux)
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### "pySerial not installed"
```bash
pip install pyserial
# or
python -m pip install pyserial
```

### GUI won't start
1. Verify Python version: `python --version` (need 3.7+)
2. Test tkinter: `python -m tkinter`
3. Check for errors: Run directly with `python PiSlide_GUI.py`

### E-STOP doesn't work immediately
- E-STOP triggers between motion commands
- Motors may complete current move before stopping
- If unresponsive, close the window or use Task Manager/System Monitor

---

## Technical Details

### Motion Control Workflow
1. Connect to Marlin via serial
2. Home Y-axis (endstop detection)
3. For each cycle:
   - Move +2610mm (relative positioning)
   - Pause 0.5 seconds
   - Move -2610mm
   - Take photo (trigger via M106/M107 fan commands)
4. On final cycle: Run return sequence
5. Disconnect gracefully

### Files Created/Modified
- `pislide_config.json` - Last used settings
- `log.txt` - Photo log (appended)

### Threading Model
- Main thread: GUI event loop
- Scan thread: Motion control and serial communication
- E-STOP sets flag checked between operations

---

## Command-Line Alternative

If you prefer the original command-line interface:
```bash
python PiSlide1_GUI.py
```

---

## Support

For issues or questions, refer to:
- [PiSlide1.py](PiSlide1.py) - Core scanner logic
- [Copilot Instructions](.github/copilot-instructions.md) - Architecture docs
- Port check utility: `python port_check.py`
- Endstop test: `python read_y_endstop.py`

---

## License & Credits

Part of the PiSlide film scanner project.  
Cross-platform GUI by GitHub Copilot & team.
