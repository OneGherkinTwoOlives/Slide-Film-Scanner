
import serial
from datetime import datetime, timedelta
import time
import os

# Defaults for serial connection (set to detected working values)
DEFAULT_PORT = "/dev/ttyUSB0"  # Linux: /dev/ttyUSB0 or /dev/ttyACM0; Windows: COM6
DEFAULT_BAUD = 115200

# X-axis configuration for slide positioning
MAX_X_TRAVEL = 2700  # Maximum X-axis travel in rotations
X_STEP_PER_SLIDE =100  # X-axis movement per slide (backward)
X_FEEDRATE = 30000  # Feedrate for X-axis movements



def _in_waiting(port):
    try:
        return port.in_waiting
    except AttributeError:
        try:
            return port.inWaiting()
        except Exception:
            return 0

def _read_all(port):
    read_all = getattr(port, "read_all", None)
    if callable(read_all):
        try:
            return read_all()
        except Exception:
            pass
    try:
        n = _in_waiting(port)
        if n:
            return port.read(n)
    except Exception:
        pass
    return b""

def _is_open(port):
    try:
        return port.is_open
    except AttributeError:
        try:
            return port.isOpen()
        except Exception:
            return False

def _flush_input(port):
    try:
        return port.reset_input_buffer()
    except AttributeError:
        try:
            return port.flushInput()
        except Exception:
            try:
                return port.flush()
            except Exception:
                return None

def _flush_output(port):
    try:
        return port.reset_output_buffer()
    except AttributeError:
        try:
            return port.flushOutput()
        except Exception:
            try:
                return port.flush()
            except Exception:
                return None

def MarlinWaitForReply(MarlinSerialPort: "serial.Serial", echoToPrint=True) -> bool:
    tstart = datetime.now()

    while True:
        if _in_waiting(MarlinSerialPort) > 0:
            serialString = MarlinSerialPort.readline()

            if echoToPrint:
                if serialString.startswith(b"echo:"):
                    print("Marlin R:", serialString.decode("Ascii"))

            if serialString == b"ok\n":
                return True

            tstart = datetime.now()
        else:
            duration = datetime.now()-tstart
            if duration.total_seconds() > 3:
                return False

def SendMarlinCmd(MarlinSerialPort: "serial.Serial", cmd: str) -> bool:
    if not _is_open(MarlinSerialPort):
        raise Exception("Port closed")

    _flush_input(MarlinSerialPort)
    _flush_output(MarlinSerialPort)
    _read_all(MarlinSerialPort)

    MarlinSerialPort.write(cmd.encode('utf-8'))
    MarlinSerialPort.write(b'\n')
    if MarlinWaitForReply(MarlinSerialPort) == False:
        raise Exception("Bad GCODE command or not a valid reply from Marlin")

    return True

def SendMultipleMarlinCmd(MarlinSerialPort: "serial.Serial", cmds: list) -> bool:
    for cmd in cmds:
        SendMarlinCmd(MarlinSerialPort, cmd)
    return True

def MoveFilm(marlin: "serial.Serial", y: float, feed_rate: int):
    SendMarlinCmd(marlin, "G0 Y{0:.4f} F{1}".format(y, feed_rate))
    SendMarlinCmd(marlin, "M400")

def MoveXAxis(marlin: "serial.Serial", x: float, feed_rate: int):
    """Move X-axis to specified position or distance.
    
    Args:
        marlin: Serial port connection to Marlin
        x: X-axis position (absolute) or distance (relative)
        feed_rate: Movement speed
    """
    SendMarlinCmd(marlin, "G0 X{0:.4f} F{1}".format(x, feed_rate))
    SendMarlinCmd(marlin, "M400")

def SetMarlinLight(marlin: "serial.Serial", level: int = 255):
    if level > 0:
        SendMarlinCmd(marlin, "M106 S{0}".format(level))
    else:
        SendMarlinCmd(marlin, "M107")

def ConnectToMarlin(port=DEFAULT_PORT, baudrate=DEFAULT_BAUD):
    # verify we actually imported pySerial's `serial` module
    if not hasattr(serial, "Serial"):
        mod_file = getattr(serial, "__file__", None)
        raise Exception(
            "Imported 'serial' module does not expose 'Serial'. "
            f"serial.__file__={mod_file!r}.\n" 
            "This usually means pySerial is not installed or a local file named 'serial.py' is shadowing the package."
        )
    marlin = serial.Serial(
        port=port, baudrate=baudrate, bytesize=8, timeout=5, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE
    )

    MarlinWaitForReply(marlin, False)
    SendMultipleMarlinCmd(
        marlin, ["M502", "G21", "M211 S0", "G90", "G92 X0 Y0 Z0", "M201 Y0", "M18 S15", "M203 X1000.00 Y1000.00 Z5000.00"])

    # Keep fan/light off on connect; `take_photo()` will toggle it when needed
    SetMarlinLight(marlin, 0)
    SendMarlinCmd(marlin, "M92 Y10 Z8.888888")
    SendMarlinCmd(marlin, "M400")
    return marlin

def DisconnectFromMarlin(serial_port: "serial.Serial"):
    SetMarlinLight(serial_port, 0)
    SendMultipleMarlinCmd(serial_port, ["M84"])
    serial_port.close()

def get_endstop_state(marlin: "serial.Serial", endstop_name="y_min"):
    """Check if endstop is triggered.

    This writes `M119` directly and reads all response lines until an `ok`
    or a short timeout. It avoids using `SendMarlinCmd` because that helper
    consumes the response while waiting for `ok`.
    """
    # clear any pending input, then request endstop status
    _flush_input(marlin)
    try:
        marlin.write(b"M119\n")
    except Exception:
        return "unknown"

    # collect response lines until we see 'ok' or timeout
    lines = []
    tstart = time.time()
    timeout = 2.0
    seen_ok = False
    while time.time() - tstart < timeout:
        while _in_waiting(marlin) > 0:
            raw = marlin.readline()
            try:
                line = raw.decode(errors="ignore").strip()
            except Exception:
                line = str(raw)
            if not line:
                continue
            # some firmwares send 'ok' as reply terminator
            if line.lower() == 'ok':
                seen_ok = True
                break
            lines.append(line)
        if seen_ok:
            break
        time.sleep(0.05)

    # parse M119 output for the requested endstop
    for line in lines:
        if endstop_name in line.lower():
            l = line.lower()
            # Invert meaning: Marlin's 'TRIGGERED' -> treat as 'open', 'open' -> treat as 'triggered'
            if 'triggered' in l:
                print("Endstop state: open (still open....)")
                return "open"
            if 'open' in l:
                print("Endstop state: triggered (inverted from open)")
                return "triggered"

    return "unknown"

def home_y_axis(marlin: "serial.Serial", move_fast=30000, move_slow=2500, initial_move=20, endstop_name="y_min"):
    """Home the Y axis by moving until endstop is triggered."""
    print("Starting Y axis homing routine...")
    
    # Relative positioning
    SendMarlinCmd(marlin, "G91")
    
    # Make sure motors are enabled
    SendMarlinCmd(marlin, "M17")
    
    # Initial move in positive Y direction
    print("Initial Y move...")
    SendMarlinCmd(marlin, f"G1 Y{initial_move} F{move_fast}")
    time.sleep(0.5)
    
    # Reverse direction and search for endstop
    print(f"Searching for {endstop_name} endstop...")
    trigger = get_endstop_state(marlin, endstop_name)
    
    while trigger != "triggered":
        SendMarlinCmd(marlin, f"G1 Y-5 F{move_slow}")
        time.sleep(0.2)
        trigger = get_endstop_state(marlin, endstop_name)
    
    print("Endstop triggered!")
    print(f"Endstop triggered! Moving back by {initial_move+20} mm...")
    SendMarlinCmd(marlin, f"G1 Y{initial_move+20} F{move_fast}")
    SendMarlinCmd(marlin, "M400")  # Wait for motion to complete
    print("Pausing 0.5 seconds...")
    time.sleep(0.5)
    
    # Zero Y axis
    SendMarlinCmd(marlin, "G92 Y0")
    
    # Switch back to absolute positioning
    SendMarlinCmd(marlin, "G90")
    
    print("Y axis homed successfully")

def get_last_log_entry(log_file_path: str):
    """Read the last line from the log file and parse photo number, description, and year.
    
    Returns tuple (photo_number, description, year) or (None, None, None) if file doesn't exist or can't be parsed.
    Format: photo_number|description|year
    """
    try:
        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()
            if not lines:
                return (None, None, None)
            
            # Get the last non-empty line
            last_line = None
            for line in reversed(lines):
                if line.strip():
                    last_line = line.strip()
                    break
            
            if not last_line:
                return (None, None, None)
            
            # Parse new format: "photo_number|description|year"
            if '|' in last_line:
                parts = last_line.split('|')
                if len(parts) >= 2:
                    try:
                        photo_number = int(parts[0].strip())
                        description = parts[1].strip()
                        year = parts[2].strip() if len(parts) >= 3 else None
                        return (photo_number, description, year)
                    except (ValueError, IndexError):
                        return (None, None, None)
            
            # Fallback: Parse old format "Photo #123: Description Year" for backward compatibility
            if last_line.startswith("Photo #"):
                parts = last_line.split(": ", 1)
                if len(parts) == 2:
                    photo_part = parts[0].replace("Photo #", "").strip()
                    description = parts[1].strip()
                    # Try to extract year from end of description
                    desc_parts = description.rsplit(' ', 1)
                    year = None
                    if len(desc_parts) == 2 and desc_parts[1].startswith('19') and len(desc_parts[1]) == 4 and desc_parts[1].isdigit():
                        description = desc_parts[0]
                        year = desc_parts[1]
                    try:
                        photo_number = int(photo_part)
                        return (photo_number, description, year)
                    except ValueError:
                        return (None, None, None)
            
            return (None, None, None)
    except FileNotFoundError:
        return (None, None, None)
    except Exception as e:
        print(f"Warning: Could not read log file: {e}")
        return (None, None, None)

def log_photo(photo_number: int, description: str, log_file_path: str):
    """Append a photo entry to the log file.
    
    Format: photo_number|description|year
    Parses year from end of description if present (format: 'description 19XX')
    """
    try:
        # Extract year from description if present
        year = ""
        desc_parts = description.rsplit(' ', 1)
        if len(desc_parts) == 2 and desc_parts[1].startswith('19') and len(desc_parts[1]) == 4 and desc_parts[1].isdigit():
            description = desc_parts[0]
            year = desc_parts[1]
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"{photo_number}|{description}|{year}\n")
    except Exception as e:
        print(f"Warning: Failed to write to log file: {e}")

def take_photo(marlin: "serial.Serial", photo_number: int = None, description: str = None, log_file_path: str = None, shutter_time: float = 1.0):
    """Turn fan on to trigger photo, wait, then turn it off.

    Uses `SetMarlinLight` which sends `M106`/`M107` commands.
    If photo_number, description, and log_file_path are provided, logs the photo.
    """
    try:
        SetMarlinLight(marlin, 255)
        print("I taka da photo")
        time.sleep(shutter_time)
        
        # Log the photo if logging parameters are provided
        if photo_number is not None and description is not None and log_file_path is not None:
            log_photo(photo_number, description, log_file_path)
            print(f"Logged photo #{photo_number}")
    finally:
        SetMarlinLight(marlin, 0)
        time.sleep(0.2)
        print("ey done, ya?!")

def return_last(marlin: "serial.Serial", distance: float, feed_rate: int):
    """Move motor 1/2 distance positive, then 1/2 distance negative.
    
    Called after the last cycle to return to starting position.
    """
    half_distance = (distance / 2)+400
    print(f"Returning: moving +{half_distance} mm...")
    MoveFilm(marlin, half_distance, feed_rate)
    print(f"Returning: moving -{half_distance} mm...")
    MoveFilm(marlin, -half_distance, feed_rate)
    print("Return sequence complete")

def main():
    global lower_threshold, shutter_speed, iso


    STANDARD_FEED_RATE = 100000

    # Prompt for serial port so script works on Windows (e.g. COM3)
    port_input = DEFAULT_PORT
    # input(f"Serial port (press Enter for {DEFAULT_PORT}): ")
    port = port_input.strip() if port_input.strip() != "" else DEFAULT_PORT

    # Prompt for baud rate
    # baud_input = DEFAULT_BAUD 
    # input(f"Baud rate (press Enter for {DEFAULT_BAUD}): ")
    # try:
    #     baudrate = int(baud_input) if baud_input.strip() != "" else DEFAULT_BAUD
    # except Exception:
    #     print(f"Invalid baud rate; using {DEFAULT_BAUD}")
    baudrate = DEFAULT_BAUD

    
    # distance in millimeters to move on each cycle
    distance = 2550

    # Create log file path in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "log.txt")
    print(f"Log file: {log_file_path}")
    
    # Check if log file exists and offer to continue from last entry
    description = None
    last_photo_no = None
    
    if os.path.exists(log_file_path):
        last_photo_no_from_log, description_from_log, year_from_log = get_last_log_entry(log_file_path)
        
        if last_photo_no_from_log is not None and description_from_log is not None:
            print(f"\nLog file found with last entry:")
            print(f"  Photo #{last_photo_no_from_log}: {description_from_log}")
            continue_response = input(f"Continue from: Photo #{last_photo_no_from_log} - {description_from_log} [y/n]? ").strip().lower()
            
            if continue_response in ['y', 'yes', '']:
                # Use values from log file
                last_photo_no = last_photo_no_from_log
                description = description_from_log
                print(f"Continuing from photo #{last_photo_no}\n")
    
    # If not continuing from log file, get user input
    if description is None or last_photo_no is None:
        description = input("Provide Description (year, place, etc.): ").strip()
        if not description:
            description = "No description provided"
        
        last_photo_no_input = input("What is the last picture number?: ").strip()
        try:
            last_photo_no = int(last_photo_no_input) if last_photo_no_input else 0
        except ValueError:
            print("Invalid photo number; starting from 0")
            last_photo_no = 0

    # Get number of cycles from user
    cycles_input = input("Number of movement cycles (default 1): ")
    try:
        num_cycles = int(cycles_input) if cycles_input.strip() != "" else 1
    except Exception:
        print("Invalid input; using 1 cycle")
        num_cycles = 1
    
    # Validate X-axis travel limits
    max_slides = MAX_X_TRAVEL // X_STEP_PER_SLIDE
    if num_cycles > max_slides:
        print(f"\nERROR: Requested {num_cycles} cycles exceeds maximum X-axis travel!")
        print(f"Maximum slides available: {max_slides} (total travel: {MAX_X_TRAVEL}, step per slide: {X_STEP_PER_SLIDE})")
        print("Exiting program.")
        return
    
    # Calculate remaining X travel
    remaining_x_travel = MAX_X_TRAVEL - (num_cycles * X_STEP_PER_SLIDE)
    print(f"\nX-axis travel plan:")
    print(f"  Total available: {MAX_X_TRAVEL} rotations")
    print(f"  Required for {num_cycles} slides: {num_cycles * X_STEP_PER_SLIDE} rotations")
    print(f"  Remaining after completion: {remaining_x_travel} rotations")

    marlin = ConnectToMarlin(port, baudrate)

    # Home the Y axis before starting
    home_y_axis(marlin)
    
    # Initialize X-axis to starting position
    print(f"\nMoving X-axis to starting position (+{MAX_X_TRAVEL} rotations)...")
    SendMarlinCmd(marlin, "G90")  # Ensure absolute positioning
    MoveXAxis(marlin, MAX_X_TRAVEL, X_FEEDRATE)
    current_x_position = MAX_X_TRAVEL
    print(f"X-axis at position: {current_x_position}")

    # Start automated movement cycle
    print(f"\nStarting {num_cycles} cycles of movement...")
    print(f"Each cycle: +{distance} mm, pause 0.5s, -{distance} mm")
    
    try:
        # Switch to relative positioning for the movement cycles
        SendMarlinCmd(marlin, "G91")
        
        # Track current photo number
        current_photo_no = last_photo_no
        
        for cycle in range(1, num_cycles + 1):
            print(f"\n--- Cycle {cycle} of {num_cycles} ---")

            # Move in positive direction
            print(f"Moving +{distance} mm...")
            MoveFilm(marlin, distance, STANDARD_FEED_RATE)  

            # Move X-axis backward for next slide (skip on first cycle)
            if cycle > 1:
                print(f"Moving X-axis -{X_STEP_PER_SLIDE} rotations...")
                # Temporarily switch to absolute positioning for X-axis
                SendMarlinCmd(marlin, "G90")
                current_x_position -= X_STEP_PER_SLIDE
                MoveXAxis(marlin, current_x_position, X_FEEDRATE)
                # Switch back to relative positioning for Y-axis cycles
                SendMarlinCmd(marlin, "G91")
                print(f"X-axis now at position: {current_x_position}")
                print(f"Remaining X travel: {current_x_position} rotations")
            

            
            # Pause
            print("Pausing 0.5 seconds...")
            time.sleep(0.5)
            
            # Move in negative direction
            print(f"Moving -{distance} mm...")
            MoveFilm(marlin, -distance, STANDARD_FEED_RATE)
            
            print(f"Cycle {cycle} complete")

            # Take photo at completion of this cycle
            try:
                current_photo_no += 1
                take_photo(marlin, current_photo_no, description, log_file_path)
            except Exception as e:
                print(f"take_photo failed: {e}")
            
            # Run return_last on the final cycle only
            if cycle == num_cycles:
                try:
                    return_last(marlin, distance, STANDARD_FEED_RATE)
                except Exception as e:
                    print(f"return_last failed: {e}")
        
        # Return to absolute positioning
        SendMarlinCmd(marlin, "G90")
        
        # Return X-axis to home position (0)
        print(f"\nReturning X-axis to home position (0)...")
        MoveXAxis(marlin, 0, X_FEEDRATE)
        print(f"X-axis returned to home position")
        
        print(f"\nAll {num_cycles} cycles completed successfully!")
        
    finally:
        print("Disconnect Marlin")
        DisconnectFromMarlin(marlin)


if __name__ == "__main__":
    main()
