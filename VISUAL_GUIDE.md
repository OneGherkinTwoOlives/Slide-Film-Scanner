# PiSlide Scanner GUI - Visual Guide

## 🎯 What You Get

A modern desktop application to control your PiSlide film scanner:

```
╔═══════════════════════════════════════════════════════╗
║            PiSlide Film Scanner                       ║
╠═══════════════════════════════════════════════════════╣
║  📋 Scan Configuration                                ║
║  ┌─────────────────────────────────────────────────┐  ║
║  │ Description:   [Summer 1985] [Use Last      ]  │  ║
║  │ Last Photo #:  [45         ] [Continue from  ]  │  ║
║  │                                [Last         ]  │  ║
║  │ Number of Cycles: [20]                          │  ║
║  │ Serial Port:      [COM6]                        │  ║
║  └─────────────────────────────────────────────────┘  ║
║                                                        ║
║       [🟢 START SCAN]         [🔴 E-STOP]            ║
║                                                        ║
║  📊 Status                                             ║
║  ┌─────────────────────────────────────────────────┐  ║
║  │ [10:30:15] Connected successfully!              │  ║
║  │ [10:30:16] Homing Y axis...                     │  ║
║  │ [10:30:20] Y axis homed successfully            │  ║
║  │ [10:30:21] Starting 20 cycles...                │  ║
║  │ [10:30:22] --- Cycle 1 of 20 ---                │  ║
║  │ [10:30:23] Moving +2610mm...                    │  ║
║  │ [10:30:35] Moving -2610mm...                    │  ║
║  │ [10:30:47] Photo #46 captured ✓                 │  ║
║  │ [10:30:48] --- Cycle 2 of 20 ---                │  ║
║  │ ...                                             │  ║
║  └─────────────────────────────────────────────────┘  ║
║  [████████████████░░░░░░░░░░░░] 65%                   ║
║              Cycle 13/20                              ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🪟 Windows - Getting Started

### Step 1: Create Desktop Shortcut
Double-click: `create_desktop_shortcut.bat`

```
💾 create_desktop_shortcut.bat  ← Double-click this
```

This creates an icon on your desktop called "PiSlide Scanner"

### Step 2: Launch the GUI
Double-click the desktop icon or `launch_pislide_gui.bat`

```
🖼️ PiSlide Scanner  ← Double-click this
```

---

## 🐧 Linux - Getting Started

### Step 1: Make Launcher Executable
Open terminal in the SlideScanner folder:
```bash
chmod +x launch_pislide_gui.sh
```

### Step 2: Launch the GUI
```bash
./launch_pislide_gui.sh
```

### Step 3: Create Desktop Icon (Optional)
```bash
# Edit the desktop file
nano PiSlide.desktop
# Replace %INSTALL_DIR% with your actual path

# Install it
cp PiSlide.desktop ~/.local/share/applications/
```

---

## 📝 Using the GUI

### Scenario 1: Starting a New Batch

```
1. Enter Description: "Summer 1985, Vermont"
2. Set Last Photo #: 0
3. Set Number of Cycles: 20
4. Click START SCAN
```

### Scenario 2: Continuing Previous Batch

```
1. Click [Continue from Last]
   → Auto-fills both Description and Photo #
2. Set Number of Cycles: 20
3. Click START SCAN
```

### Scenario 3: Same Description, New Photos

```
1. Click [Use Last] next to Description
   → Loads "Summer 1985, Vermont"
2. Manually set Last Photo #: 100
3. Set Number of Cycles: 20
4. Click START SCAN
```

---

## 🎛️ Control Flow

### Starting a Scan

```
You click [START SCAN]
         ↓
GUI validates inputs (must be numbers, etc.)
         ↓
Saves your settings to pislide_config.json
         ↓
Disables START button, enables E-STOP
         ↓
Connects to Marlin over serial port
         ↓
Homes Y axis (finds reference point)
         ↓
Runs movement cycles:
    Move forward → Pause → Move back → Take photo
         ↓
After last cycle: Return to start position
         ↓
Disconnects from Marlin
         ↓
Re-enables START button
```

### Emergency Stop

```
You click [E-STOP]
         ↓
Sets stop flag
         ↓
Current motion completes (for safety)
         ↓
No more cycles run
         ↓
Attempts graceful disconnect
         ↓
Re-enables START button
```

---

## 🎨 Status Colors

The status window uses colors to help you quickly see what's happening:

- **🔵 Blue (Info)**: Normal operations ("Connecting...", "Moving +2610mm...")
- **🟢 Green (Success)**: Completed successfully ("Photo #5 captured", "Homed successfully")
- **🟠 Orange (Warning)**: Non-critical issues ("No previous log entry found")
- **🔴 Red (Error)**: Problems ("Serial port not found", "E-STOP REQUESTED")

---

## 💾 Files Created

### pislide_config.json
Your last settings are saved here:
```json
{
  "description": "Summer 1985, Vermont",
  "last_photo": "45",
  "cycles": "20",
  "port": "COM6",
  "timestamp": "2025-12-28T10:30:00"
}
```

### log.txt
Every photo is logged:
```
Photo #1: Summer 1985, Vermont
Photo #2: Summer 1985, Vermont
Photo #3: Summer 1985, Vermont
...
Photo #45: Summer 1985, Vermont
Photo #46: Beach Trip 1987
Photo #47: Beach Trip 1987
```

Both files are in the same folder as the GUI application.

---

## ⚡ Quick Tips

### Tip 1: Resume After Power Loss
If something interrupts your scan:
1. Relaunch GUI
2. Click "Continue from Last"
3. Click START SCAN

The GUI remembers where you left off!

### Tip 2: Check Setup First
Before your first run:
```bash
python test_gui_setup.py
```
This verifies all dependencies are installed.

### Tip 3: Change Serial Port
If your Arduino is on a different port:
- Windows: Check Device Manager → Ports (COM & LPT)
- Linux: Run `ls /dev/ttyUSB* /dev/ttyACM*`

Update the "Serial Port" field in the GUI.

### Tip 4: Keep Console Closed
The launchers (.bat and .sh) hide the console window.
The GUI shows everything you need in the Status area.

---

## ❓ Quick Troubleshooting

### "Serial port not found"
```
Solution: Check cable, verify port name in Device Manager/terminal
```

### "pySerial not installed"
```bash
pip install pyserial
```

### "Permission denied" (Linux only)
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### E-STOP not responding immediately
```
This is normal - it completes the current move first for safety
```

### Window won't close during scan
```
This is intentional! Use E-STOP first, then close.
```

---

## 🔄 GUI vs Command Line

| Feature | GUI | Old CLI |
|---------|-----|---------|
| Interface | Buttons & forms | Type commands |
| Stop scan | E-STOP button | Ctrl-C |
| Remember settings | Automatic | Re-type every time |
| See progress | Progress bar | Text only |
| Status | Color-coded log | Plain text |
| Launch | Desktop icon | Terminal command |

**Both work!** Use whichever you prefer. The GUI just makes it easier.

---

## 📚 More Help

- **Quick reference**: See [QUICK_START.md](QUICK_START.md)
- **Full manual**: See [GUI_README.md](GUI_README.md)
- **File guide**: See [FILE_STRUCTURE.md](FILE_STRUCTURE.md)
- **What's new**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🎉 You're Ready!

That's it! You now have a user-friendly GUI for your PiSlide scanner.

**Next steps:**
1. Run `test_gui_setup.py` to check everything
2. Create desktop shortcut (Windows) or launcher (Linux)
3. Double-click to start scanning!

Happy scanning! 📸
