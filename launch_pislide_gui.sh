#!/bin/bash
# PiSlide Scanner GUI Launcher for Linux
# Make executable with: chmod +x launch_pislide_gui.sh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting PiSlide Scanner GUI..."

# Try to use python3, fall back to python
if command -v python3 &> /dev/null; then
    python3 PiSlide_GUI.py
elif command -v python &> /dev/null; then
    python PiSlide_GUI.py
else
    echo "Error: Python not found!"
    echo "Please install Python 3 and try again."
    read -p "Press Enter to close..."
    exit 1
fi

# If there was an error, pause so user can see it
if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred."
    read -p "Press Enter to close..."
fi
