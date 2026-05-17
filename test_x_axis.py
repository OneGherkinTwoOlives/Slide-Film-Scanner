#!/usr/bin/env python3
"""
X/Y-Axis Test Script for PiSlide
Test both X and Y axis movement with configurable distances
"""

import sys
import time
from PiSlide1_GUI import (
    ConnectToMarlin,
    DisconnectFromMarlin,
    SendMarlinCmd,
    DEFAULT_PORT,
    DEFAULT_BAUD
)

# Distance for one motor rotation (adjust based on your motor/pulley setup)
# Common values: 20mm for GT2 belt with 20-tooth pulley
ROTATION_DISTANCE = 200  # mm per rotation

def move_x_axis(marlin, distance, feed_rate=12000):
    """Move X-axis by specified distance."""
    print(f"Moving X-axis {distance}mm...")
    SendMarlinCmd(marlin, f"G0 X{distance} F{feed_rate}")
    SendMarlinCmd(marlin, "M400")  # Wait for move to complete
    print("Move complete")

def move_y_axis(marlin, distance, feed_rate=60000):
    """Move Y-axis by specified distance."""
    print(f"Moving Y-axis {distance}mm...")
    SendMarlinCmd(marlin, f"G0 Y{distance} F{feed_rate}")
    SendMarlinCmd(marlin, "M400")  # Wait for move to complete
    print("Move complete")

def main():
    print("=" * 50)
    print("PiSlide X/Y-Axis Test")
    print("=" * 50)
    print(f"X-axis rotation distance: {ROTATION_DISTANCE}mm")
    print()
    
    # Get Y-axis distance from user
    y_distance = None
    while y_distance is None:
        try:
            user_input = input("Enter Y-axis movement distance (mm) [default: 100]: ").strip()
            if user_input == "":
                y_distance = 100.0
            else:
                y_distance = float(user_input)
                if y_distance <= 0:
                    print("Distance must be positive. Please try again.")
                    y_distance = None
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    print(f"Y-axis movement distance: {y_distance}mm")
    print()
    
    # Connect to Marlin
    try:
        print(f"Connecting to Marlin on {DEFAULT_PORT}...")
        marlin = ConnectToMarlin(DEFAULT_PORT, DEFAULT_BAUD)
        print("Connected successfully!")
        print()
    except Exception as e:
        print(f"ERROR: Could not connect to Marlin: {e}")
        return 1
    
    try:
        # Initialize axes
        print("Initializing axes...")
        SendMarlinCmd(marlin, "G91")  # Relative positioning
        SendMarlinCmd(marlin, "G92 X0 Y0")  # Set current position as zero
        print("Axes ready")
        print()
        print("Controls:")
        print("  Press 'x' + ENTER to move X-axis forward")
        print("  Press 'X' + ENTER to move X-axis backward")
        print("  Press 'y' + ENTER to move Y-axis forward")
        print("  Press 'Y' + ENTER to move Y-axis backward")
        print("  Press 'q' + ENTER to quit")
        print("-" * 50)
        
        total_x_distance = 0
        total_y_distance = 0
        
        while True:
            try:
                user_input = input("Command: ").strip()
                
                if user_input == 'x':
                    move_x_axis(marlin, ROTATION_DISTANCE)
                    total_x_distance += ROTATION_DISTANCE
                    print(f"Total X distance: {total_x_distance}mm, Total Y distance: {total_y_distance}mm\n")
                    
                elif user_input == 'X':
                    move_x_axis(marlin, -ROTATION_DISTANCE)
                    total_x_distance -= ROTATION_DISTANCE
                    print(f"Total X distance: {total_x_distance}mm, Total Y distance: {total_y_distance}mm\n")
                    
                elif user_input == 'y':
                    move_y_axis(marlin, y_distance)
                    total_y_distance += y_distance
                    print(f"Total X distance: {total_x_distance}mm, Total Y distance: {total_y_distance}mm\n")
                    
                elif user_input == 'Y':
                    move_y_axis(marlin, -y_distance)
                    total_y_distance -= y_distance
                    print(f"Total X distance: {total_x_distance}mm, Total Y distance: {total_y_distance}mm\n")
                    
                elif user_input.lower() == 'q':
                    print("Quitting...")
                    break
                    
                else:
                    print("Invalid command. Use 'x', 'X', 'y', 'Y' to move, or 'q' to quit.\n")
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
                
    finally:
        print("\nDisconnecting from Marlin...")
        try:
            SendMarlinCmd(marlin, "G90")  # Back to absolute positioning
            DisconnectFromMarlin(marlin)
            print("Disconnected successfully")
        except Exception as e:
            print(f"Error during disconnect: {e}")
    
    print("Test complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
