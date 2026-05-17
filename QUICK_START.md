# PiSlide Scanner GUI - Quick Start

## Windows Users

### First Time Setup:
1. Double-click `create_desktop_shortcut.bat` to create a desktop icon
   
### Every Time:
1. Double-click the "PiSlide Scanner" desktop icon (or `launch_pislide_gui.bat`)
2. Fill in the form:
   - **Description**: "Summer 1985, Vermont" 
   - **Last Photo #**: 0 (or click "Continue from Last")
   - **Number of Cycles**: 20
3. Click **START SCAN**
4. Watch the status window for progress
5. Use **E-STOP** if you need to abort

---

## Linux Users

### First Time Setup:
```bash
cd /path/to/SlideScanner
chmod +x launch_pislide_gui.sh
```

Optional - Create desktop icon:
```bash
# Edit PiSlide.desktop - replace %INSTALL_DIR% with your actual path
nano PiSlide.desktop

# Install the desktop file
cp PiSlide.desktop ~/.local/share/applications/
```

### Every Time:
```bash
./launch_pislide_gui.sh
```
Or double-click the desktop icon if you created one.

---

## Tips

💡 **Use Last Button**: Recalls the last description from your log  
💡 **Continue from Last**: Automatically loads last photo number AND description  
💡 **Serial Port**: Leave as default (COM6 or /dev/ttyUSB0) unless you changed it  
💡 **E-STOP**: Red emergency stop button - same as pressing Ctrl-C  
💡 **Log File**: All photos are logged to `log.txt` automatically  

---

## Common Issues

❌ **"pySerial not installed"**  
```bash
pip install pyserial
```

❌ **"Serial port not found"**  
- Windows: Check Device Manager for COM port number
- Linux: Try `/dev/ttyUSB0` or `/dev/ttyACM0`

❌ **"Permission denied" (Linux)**  
```bash
sudo usermod -a -G dialout $USER
# Then log out and back in
```

---

For detailed documentation, see [GUI_README.md](GUI_README.md)
