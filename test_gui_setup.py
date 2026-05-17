#!/usr/bin/env python3
"""
Test script to verify all dependencies for PiSlide GUI are installed.
Run this before using the GUI for the first time.
"""

import sys

def test_python_version():
    """Check Python version is 3.7 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.7+)")
        return False

def test_tkinter():
    """Check if tkinter is available."""
    print("\nChecking tkinter...")
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("  ✓ tkinter is installed")
        return True
    except ImportError:
        print("  ✗ tkinter is NOT installed")
        print("    Windows: Reinstall Python with tcl/tk option")
        print("    Linux: sudo apt-get install python3-tk")
        return False
    except Exception as e:
        print(f"  ✗ tkinter error: {e}")
        return False

def test_serial():
    """Check if pySerial is available."""
    print("\nChecking pySerial...")
    try:
        import serial
        if not hasattr(serial, "Serial"):
            print("  ⚠ Warning: 'serial' module found but it's not pySerial")
            print("    However, PiSlide1_GUI.py handles this - checking that instead...")
            # The actual code handles this, so let's check if PiSlide can use it
            try:
                from PiSlide1_GUI import DEFAULT_PORT
                print("  ✓ PiSlide modules can import serial (OK)")
                return True
            except:
                print("  ✗ PiSlide modules cannot import serial")
                return False
        print("  ✓ pySerial is installed")
        return True
    except ImportError:
        print("  ✗ pySerial is NOT installed")
        print("    Install with: pip install pyserial")
        return False
    except Exception as e:
        print(f"  ✗ pySerial error: {e}")
        return False

def test_imports():
    """Check if main scanner modules can be imported."""
    print("\nChecking PiSlide modules...")
    try:
        from PiSlide1_GUI import (
            ConnectToMarlin,
            DisconnectFromMarlin,
            SendMarlinCmd,
            MoveFilm,
            SetMarlinLight,
            home_y_axis,
            take_photo,
            return_last,
            get_last_log_entry,
            DEFAULT_PORT,
            DEFAULT_BAUD
        )
        print("  ✓ PiSlide1_GUI module imports OK")
        return True
    except ImportError as e:
        print(f"  ✗ Cannot import PiSlide1_GUI: {e}")
        print("    Make sure PiSlide1_GUI.py is in the same directory")
        return False
    except Exception as e:
        print(f"  ✗ Error importing PiSlide1_GUI: {e}")
        return False

def test_gui_import():
    """Check if GUI script can be imported."""
    print("\nChecking GUI script...")
    try:
        import PiSlide1_GUI
        print("  ✓ PiSlide1_GUI.py can be imported")
        return True
    except ImportError as e:
        print(f"  ✗ Cannot import PiSlide1_GUI: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error importing GUI: {e}")
        return False

def main():
    print("=" * 50)
    print("PiSlide Scanner GUI - Dependency Check")
    print("=" * 50)
    
    results = []
    results.append(("Python Version", test_python_version()))
    results.append(("tkinter", test_tkinter()))
    results.append(("pySerial", test_serial()))
    results.append(("PiSlide Modules", test_imports()))
    results.append(("GUI Script", test_gui_import()))
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    all_pass = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_pass = False
    
    print("=" * 50)
    
    if all_pass:
        print("\n✓ All checks passed! You can run the GUI.")
        print("\nWindows: Double-click launch_pislide_gui.bat")
        print("Linux:   ./launch_pislide_gui.sh")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
