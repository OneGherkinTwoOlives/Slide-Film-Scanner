# Copilot Instructions for PiSlide Film Scanner

## Project Overview
PiSlide is a motion-controlled film slide digitization system. It uses Marlin firmware (3D printer firmware) running on an Arduino/ESP32 to automate precise Y-axis movement of film across a camera/scanner. The system coordinates motion control (G-code), endstop homing, and light/fan triggering for automated photo capture.

## Architecture & Key Components

### Serial Communication Layer (`PiSlide1.py`)
- **Protocol**: Marlin G-code over USB serial (COM6, 115200 baud by default)
- **Key Abstraction**: `SendMarlinCmd()` sends commands and waits for "ok" replies with 3-second timeout
- **Robustness Pattern**: Helper functions (`_in_waiting()`, `_is_open()`, `_flush_input()`, etc.) handle compatibility across Python serial library versions
- **Critical Pattern**: Always flush I/O buffers before sending commands and reading replies to avoid protocol desync
- **Example**: [Marlin command sequence](PiSlide1.py#L130-L140)

### Core Motion Control
- **Home Y-axis** (`home_y_axis()`): Uses endstop detection to establish reference point
  - Relative positioning (G91), initial move, then searches backward until endstop triggered
  - Inverts Marlin semantics: "TRIGGERED" in response means open, "open" means triggered
- **Move film** (`MoveFilm()`): Absolute positioning, calls `M400` to wait for completion
- **Light/fan control** (`SetMarlinLight()`): `M106` (on) / `M107` (off) commands; fan doubles as photo trigger

### Hardware Interface (Arduino/ESP32)
- [SimpleWiFiServerFADE.ino](Arduino/SimpleWiFiServerFADE/SimpleWiFiServerFADE.ino): ESP32 WiFi web server for LED/fan PWM control
- Uses LEDC PWM (5kHz, 8-bit resolution) for smooth fading

## Critical Workflows

### Scanning Workflow (`main()` in PiSlide1.py)
1. Connect to Marlin via serial (validates pySerial import)
2. Home Y-axis (establish reference)
3. Execute N cycles of: +distance mm → pause 0.5s → -distance mm → take photo
4. Disconnect safely

### Testing/Debugging Utilities
- **port_check.py**: Validates serial port access and pySerial availability
- **read_y_endstop.py**: Tests M119 command and endstop interpretation
- **fan_test.py**: Basic M106/M107 fan on/off test
- **Homing_Routine1.py**: Standalone homing without full scanning (useful for isolation testing)

### Marlin Initialization Sequence
```python
["M502",           # Load defaults
 "G21",            # mm units
 "M211 S0",        # Disable soft limits
 "G90",            # Absolute positioning
 "G92 X0 Y0 Z0",   # Set origin
 "M201 Y0",        # Disable acceleration
 "M18 S15",        # Auto-disable steppers after 15s
 "M203 X1000 Y1000 Z5000",  # Max speeds
 "M92 Y10 Z8.888"]  # Steps/mm (Y:10, Z:8.888)
```

## Project Conventions & Patterns

### Error Handling
- Marlin failures throw exceptions (don't return error codes)
- Serial timeouts → exception in `MarlinWaitForReply()`
- Always wrap motor operations in try/finally to ensure `DisconnectFromMarlin()` runs

### Configuration
- **Defaults**: `DEFAULT_PORT="COM6"`, `DEFAULT_BAUD=115200`
- **Motion**: `STANDARD_FEED_RATE=60000` mm/min (edit in main())
- **Distance**: `distance=2650` mm per cycle (edit in main())
- **Endstops**: Configured for `y_min`; change in homing function if needed

### Serial Port Compatibility
- Code handles both new pySerial (`reset_input_buffer()`) and legacy (`flushInput()`) APIs
- Windows uses `COM*` ports; Linux uses `/dev/ttyUSB*` or `/dev/ttyACM*`
- Check with port_check.py if connections fail

## External Dependencies
- **pySerial**: Serial communication (`python -m pip install pyserial`)
- **numpy**: Imported but not actively used in current code (legacy)
- **Marlin firmware**: Running on Arduino/ESP32 with specific G-code support (M106, M119, M400)

## Key Files Reference
- [PiSlide1.py](PiSlide1.py) — Main scanner orchestration
- [Homing_Routine1.py](Homing_Routine1.py) — Standalone homing test (simpler than full PiSlide1)
- [SimpleWiFiServerFADE.ino](Arduino/SimpleWiFiServerFADE/SimpleWiFiServerFADE.ino) — WiFi LED control

## Common Pitfalls
1. **Endstop logic inversion**: Marlin's "TRIGGERED" state is semantically inverted in this codebase
2. **Buffer bloat**: Failing to flush I/O before/after commands causes "ok" misalignment
3. **Port not closed**: Missing `DisconnectFromMarlin()` leaves serial port locked; restart IDE if stuck
4. **pySerial shadow**: Local file named `serial.py` breaks import; `port_check.py` diagnoses this
