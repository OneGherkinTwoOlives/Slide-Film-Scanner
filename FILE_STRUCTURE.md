# PiSlide Scanner - File Structure

```
SlideScanner/
│
├── 📱 GUI APPLICATION FILES
│   ├── PiSlide_GUI.py                    # Main GUI application (NEW)
│   ├── PiSlide1_GUI.py                   # Core scanner functions
│   │
│   ├── 🪟 Windows Launchers
│   │   ├── launch_pislide_gui.bat        # Double-click to run GUI
│   │   └── create_desktop_shortcut.bat   # Create desktop icon
│   │
│   └── 🐧 Linux Launchers
│       ├── launch_pislide_gui.sh         # Shell script to run GUI
│       └── PiSlide.desktop               # Desktop file for icon
│
├── 📚 DOCUMENTATION
│   ├── GUI_README.md                     # Complete GUI documentation (NEW)
│   ├── QUICK_START.md                    # Quick start guide (NEW)
│   └── PiSlide Change Log.md             # Project change log
│
├── 🔧 UTILITIES
│   ├── test_gui_setup.py                 # Dependency checker (NEW)
│   ├── port_check.py                     # Serial port tester
│   ├── read_y_endstop.py                 # Endstop tester
│   ├── fan_test.py                       # Fan/light tester
│   └── Homing_Routine1.py                # Standalone homing test
│
├── 📜 LEGACY COMMAND-LINE VERSIONS
│   ├── PiSlide1.py                       # Original CLI version
│   ├── PiSlide1_Lin.py                   # Linux version
│   ├── PiSlide1_LinLog1.py               # With logging v1
│   └── PiSlide1_LinLog2.py               # With logging v2
│
├── 📊 RUNTIME FILES (created automatically)
│   ├── log.txt                           # Photo log (created on first run)
│   └── pislide_config.json               # Settings cache (created on first run)
│
├── 🛠️ HARDWARE
│   └── Arduino/
│       └── SimpleWiFiServerFADE/         # ESP32 WiFi LED control
│
└── 📁 OTHER
    ├── .github/
    │   └── copilot-instructions.md       # Architecture documentation
    ├── .venv/                            # Virtual environment (optional)
    └── __pycache__/                      # Python cache (auto-generated)
```

---

## Key Files for Users

### To Run the GUI:
- **Windows**: `launch_pislide_gui.bat`
- **Linux**: `launch_pislide_gui.sh`

### To Setup:
1. Run `test_gui_setup.py` first to check dependencies
2. On Windows: Run `create_desktop_shortcut.bat` for easy access
3. On Linux: Edit and install `PiSlide.desktop`

### For Help:
- Quick help: `QUICK_START.md`
- Full documentation: `GUI_README.md`

---

## Comparison: GUI vs CLI

| Feature | GUI (PiSlide_GUI.py) | CLI (PiSlide1.py) |
|---------|---------------------|-------------------|
| User Interface | Graphical with buttons | Command-line prompts |
| Platform | Windows + Linux | Windows + Linux |
| E-Stop | Button | Ctrl-C |
| Settings Memory | Automatic (JSON) | Manual re-entry |
| "Use Last" | Button | Manual |
| "Continue from Last" | Button | Prompt-based |
| Real-time Status | Live scrolling log | Console output |
| Progress Bar | Yes | No |
| Deployment | Desktop icon | Command line |

**Recommendation**: Use the GUI for day-to-day operation. Keep CLI versions for debugging.

---

## Data Files

### pislide_config.json
Stores your last-used settings:
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
Records all photos taken:
```
Photo #1: Summer 1985, Vermont
Photo #2: Summer 1985, Vermont
Photo #3: Summer 1985, Vermont
...
```

Both files are created automatically in the same directory as the Python scripts.
