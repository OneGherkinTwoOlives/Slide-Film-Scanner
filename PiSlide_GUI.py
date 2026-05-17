#!/usr/bin/env python3
"""
PiSlide Film Scanner GUI
Cross-platform GUI for automated slide scanning with Marlin-based motion control.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import json
import os
import sys
import serial
from datetime import datetime
import time

# Import the core scanner functions from PiSlide1_GUI
from PiSlide1_GUI import (
    ConnectToMarlin,
    DisconnectFromMarlin,
    SendMarlinCmd,
    MoveFilm,
    MoveXAxis,
    SetMarlinLight,
    home_y_axis,
    take_photo,
    return_last,
    get_last_log_entry,
    DEFAULT_PORT,
    DEFAULT_BAUD,
    MAX_X_TRAVEL,
    X_STEP_PER_SLIDE,
    X_FEEDRATE
)


class RoundedButton(tk.Canvas):
    """Custom button with rounded corners."""
    def __init__(self, parent, text, command, radius=15, bg='#4a90e2', fg='white', 
                 hover_bg='#5ba3f5', font=('Helvetica', 10), padding=(20, 10), **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.command = command
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.font = font
        self.text = text
        self.padding = padding
        self.disabled = False
        self.disabled_bg = '#757575'
        self.disabled_fg = '#bdbdbd'
        
        # Get parent background color - handle both tk and ttk widgets
        try:
            parent_bg = parent['bg']
        except:
            parent_bg = '#2b2b2b'  # Default dark background
        
        # Calculate size
        temp_label = tk.Label(self, text=text, font=font)
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        self.width = text_width + padding[0] * 2
        self.height = text_height + padding[1] * 2
        
        self.configure(width=self.width, height=self.height, bg=parent_bg)
        
        self.draw_button(self.bg)
        
        # Bind events
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def draw_button(self, bg_color):
        """Draw rounded rectangle button."""
        self.delete('all')
        x0, y0, x1, y1 = 2, 2, self.width - 2, self.height - 2
        r = self.radius
        
        # Draw rounded rectangle
        self.create_arc(x0, y0, x0 + r * 2, y0 + r * 2, start=90, extent=90, 
                       fill=bg_color, outline=bg_color)
        self.create_arc(x1 - r * 2, y0, x1, y0 + r * 2, start=0, extent=90, 
                       fill=bg_color, outline=bg_color)
        self.create_arc(x0, y1 - r * 2, x0 + r * 2, y1, start=180, extent=90, 
                       fill=bg_color, outline=bg_color)
        self.create_arc(x1 - r * 2, y1 - r * 2, x1, y1, start=270, extent=90, 
                       fill=bg_color, outline=bg_color)
        self.create_rectangle(x0 + r, y0, x1 - r, y1, fill=bg_color, outline=bg_color)
        self.create_rectangle(x0, y0 + r, x1, y1 - r, fill=bg_color, outline=bg_color)
        
        # Draw text
        fg_color = self.disabled_fg if self.disabled else self.fg
        self.create_text(self.width // 2, self.height // 2, text=self.text, 
                        font=self.font, fill=fg_color)
        
    def on_enter(self, event):
        """Handle mouse enter."""
        if not self.disabled:
            self.draw_button(self.hover_bg)
            
    def on_leave(self, event):
        """Handle mouse leave."""
        if not self.disabled:
            self.draw_button(self.bg)
            
    def on_click(self, event):
        """Handle button click."""
        if not self.disabled and self.command:
            self.command()
            
    def configure_state(self, state):
        """Enable or disable button."""
        self.disabled = (state == 'disabled')
        bg_color = self.disabled_bg if self.disabled else self.bg
        self.draw_button(bg_color)


class RoundedEntry(tk.Frame):
    """Custom entry field with rounded corners."""
    def __init__(self, parent, textvariable=None, width=20, radius=10, **kwargs):
        # Get parent background color - handle both tk and ttk widgets
        try:
            parent_bg = parent['bg']
        except:
            parent_bg = '#2b2b2b'  # Default dark background
            
        tk.Frame.__init__(self, parent, bg=parent_bg)
        self.textvariable = textvariable
        self.radius = radius
        
        # Create canvas for rounded background
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=parent_bg)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Calculate dimensions
        char_width = 9  # Approximate character width
        self.width = width * char_width + 20
        self.height = 32
        self.canvas.configure(width=self.width, height=self.height)
        
        # Draw rounded rectangle
        self.draw_background('#3c3c3c')
        
        # Create entry widget
        self.entry = tk.Entry(self, textvariable=textvariable, 
                             bg='#3c3c3c', fg='#e0e0e0', 
                             insertbackground='#e0e0e0',
                             relief='flat', bd=0,
                             font=('Helvetica', 10))
        self.entry.place(x=10, y=6, width=self.width-20, height=20)
        
        # Bind focus events
        self.entry.bind('<FocusIn>', lambda e: self.draw_background('#4a5568'))
        self.entry.bind('<FocusOut>', lambda e: self.draw_background('#3c3c3c'))
        
    def draw_background(self, color):
        """Draw rounded rectangle background."""
        self.canvas.delete('bg')
        x0, y0, x1, y1 = 2, 2, self.width - 2, self.height - 2
        r = self.radius
        
        # Draw rounded rectangle
        self.canvas.create_arc(x0, y0, x0 + r * 2, y0 + r * 2, start=90, extent=90, 
                              fill=color, outline=color, tags='bg')
        self.canvas.create_arc(x1 - r * 2, y0, x1, y0 + r * 2, start=0, extent=90, 
                              fill=color, outline=color, tags='bg')
        self.canvas.create_arc(x0, y1 - r * 2, x0 + r * 2, y1, start=180, extent=90, 
                              fill=color, outline=color, tags='bg')
        self.canvas.create_arc(x1 - r * 2, y1 - r * 2, x1, y1, start=270, extent=90, 
                              fill=color, outline=color, tags='bg')
        self.canvas.create_rectangle(x0 + r, y0, x1 - r, y1, fill=color, outline=color, tags='bg')
        self.canvas.create_rectangle(x0, y0 + r, x1, y1 - r, fill=color, outline=color, tags='bg')
        
    def get(self):
        """Get entry value."""
        return self.entry.get()
        
    def insert(self, index, string):
        """Insert text into entry."""
        return self.entry.insert(index, string)


class ScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PiSlide Film Scanner")
        self.root.geometry("750x700")
        
        # Dark theme colors
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#e0e0e0',
            'bg_dark': '#1e1e1e',
            'bg_light': '#3c3c3c',
            'accent_blue': '#4a90e2',
            'accent_blue_hover': '#5ba3f5',
            'accent_green': '#4caf50',
            'accent_red': '#f44336',
            'text_secondary': '#b0b0b0',
            'border': '#505050'
        }
        
        # Apply dark theme
        self.root.configure(bg=self.colors['bg'])
        
        # Prevent window closing during scan
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # State variables
        self.marlin = None
        self.scanning = False
        self.stop_requested = False
        self.scan_thread = None
        
        # Config file for saving/loading last settings
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "pislide_config.json")
        self.log_file = os.path.join(script_dir, "log.txt")
        
        # Configure styles
        self.configure_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load last settings
        self.load_config()
    
    def configure_styles(self):
        """Configure ttk styles for modern dark theme."""
        style = ttk.Style()
        
        # Configure main frame
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['accent_blue'], font=('Helvetica', 10, 'bold'))
        
        # Entry fields
        style.configure('TEntry', fieldbackground=self.colors['bg_light'], foreground=self.colors['fg'], 
                       borderwidth=1, relief='flat')
        style.map('TEntry',
                 fieldbackground=[('focus', self.colors['bg_light'])],
                 foreground=[('focus', self.colors['fg'])])
        
        # Buttons - Default style
        style.configure('TButton',
                       background=self.colors['bg_light'],
                       foreground=self.colors['fg'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Helvetica', 9),
                       padding=8)
        style.map('TButton',
                 background=[('active', self.colors['accent_blue']), ('pressed', self.colors['accent_blue'])],
                 foreground=[('active', 'white')])
        
        # Success button (START)
        style.configure('Success.TButton',
                       background=self.colors['accent_green'],
                       foreground='white',
                       font=('Helvetica', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        style.map('Success.TButton',
                 background=[('active', '#66bb6a'), ('pressed', '#388e3c'), ('disabled', '#757575')],
                 foreground=[('disabled', '#bdbdbd')])
        
        # Danger button (E-STOP)
        style.configure('Danger.TButton',
                       background=self.colors['accent_red'],
                       foreground='white',
                       font=('Helvetica', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        style.map('Danger.TButton',
                 background=[('active', '#e57373'), ('pressed', '#d32f2f'), ('disabled', '#757575')],
                 foreground=[('disabled', '#bdbdbd')])
        
        # Accent button (Use Last, Continue)
        style.configure('Accent.TButton',
                       background=self.colors['accent_blue'],
                       foreground='white',
                       font=('Helvetica', 9),
                       borderwidth=0,
                       focuscolor='none',
                       padding=6)
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_blue_hover']), ('pressed', '#3a7bc8')])
        
        # Progress bar
        style.configure('TProgressbar',
                       background=self.colors['accent_blue'],
                       troughcolor=self.colors['bg_dark'],
                       borderwidth=0,
                       thickness=20)
        
    def create_widgets(self):
        """Create all GUI elements."""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PiSlide Film Scanner", 
                               font=('Helvetica', 18, 'bold'),
                               foreground=self.colors['accent_blue'])
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # ===== Input Section =====
        input_frame = ttk.LabelFrame(main_frame, text="Scan Configuration", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Description input with "Use Last" button
        ttk.Label(input_frame, text="Description:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        self.description_entry = RoundedEntry(input_frame, textvariable=self.description_var, width=40)
        self.description_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        use_last_btn = RoundedButton(input_frame, text="Use Last", command=self.use_last_description,
                                     bg=self.colors['accent_blue'], hover_bg=self.colors['accent_blue_hover'],
                                     padding=(15, 8))
        use_last_btn.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Year input (2 digits for 19xx years)
        ttk.Label(input_frame, text="Year:").grid(row=row, column=0, sticky=tk.W, pady=5)
        year_frame = ttk.Frame(input_frame)
        year_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(year_frame, text="19", font=('Helvetica', 10)).pack(side=tk.LEFT)
        self.year_var = tk.StringVar()
        self.year_entry = RoundedEntry(year_frame, textvariable=self.year_var, width=5)
        self.year_entry.pack(side=tk.LEFT, padx=(2, 5))
        ttk.Label(year_frame, text="(2 digits, e.g. 85 for 1985)", font=('Helvetica', 8)).pack(side=tk.LEFT)
        row += 1
        
        # Last photo number input with "Continue from Last" button
        ttk.Label(input_frame, text="Last Photo #:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.last_photo_var = tk.StringVar(value="0")
        self.last_photo_entry = RoundedEntry(input_frame, textvariable=self.last_photo_var, width=40)
        self.last_photo_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        continue_btn = RoundedButton(input_frame, text="Continue from Last", 
                                     command=self.continue_from_last,
                                     bg=self.colors['accent_blue'], hover_bg=self.colors['accent_blue_hover'],
                                     padding=(15, 8))
        continue_btn.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # Number of cycles
        ttk.Label(input_frame, text="Number of Cycles:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cycles_var = tk.StringVar(value="1")
        self.cycles_entry = RoundedEntry(input_frame, textvariable=self.cycles_var, width=40)
        self.cycles_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        row += 1
        
        # Serial Port (optional advanced setting)
        ttk.Label(input_frame, text="Serial Port:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value=DEFAULT_PORT)
        self.port_entry = RoundedEntry(input_frame, textvariable=self.port_var, width=40)
        self.port_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(input_frame, text="(Default: COM6 Win / /dev/ttyUSB0 Linux)", 
                 font=('Helvetica', 8)).grid(row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # ===== Control Buttons =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=15)
        
        self.start_btn = RoundedButton(button_frame, text="START SCAN", 
                                       command=self.start_scan,
                                       bg=self.colors['accent_green'],
                                       hover_bg='#66bb6a',
                                       font=('Helvetica', 12, 'bold'),
                                       padding=(35, 12),
                                       radius=20)
        self.start_btn.grid(row=0, column=0, padx=10)
        
        self.stop_btn = RoundedButton(button_frame, text="E-STOP", 
                                      command=self.emergency_stop,
                                      bg=self.colors['accent_red'],
                                      hover_bg='#e57373',
                                      font=('Helvetica', 12, 'bold'),
                                      padding=(35, 12),
                                      radius=20)
        self.stop_btn.grid(row=0, column=1, padx=10)
        self.stop_btn.configure_state('disabled')
        
        # ===== Emergency Platform Return (compact, inline) =====
        emergency_frame = ttk.LabelFrame(button_frame, text="Emerg Return", padding="8")
        emergency_frame.grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        
        # Config info on top
        config_info_text = f"Max:{MAX_X_TRAVEL} | Step:{X_STEP_PER_SLIDE}"
        ttk.Label(emergency_frame, text=config_info_text, 
                 font=('Helvetica', 8, 'italic'),
                 foreground=self.colors['text_secondary']).grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        # Input and button on same row
        ttk.Label(emergency_frame, text="X Pos:", font=('Helvetica', 9)).grid(row=1, column=0, sticky=tk.E, padx=(0, 3))
        self.x_position_var = tk.StringVar(value="0")
        self.x_position_entry = RoundedEntry(emergency_frame, textvariable=self.x_position_var, width=8)
        self.x_position_entry.grid(row=1, column=1, padx=3)
        
        home_btn = RoundedButton(emergency_frame, text="HOME", 
                                command=self.emergency_home_x_axis,
                                bg=self.colors['accent_red'],
                                hover_bg='#e57373',
                                font=('Helvetica', 9, 'bold'),
                                padding=(12, 6),
                                radius=10)
        home_btn.grid(row=1, column=2, padx=(3, 0))
        
        # ===== Status Display =====
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Create a frame with rounded corners for status text
        text_container = tk.Frame(status_frame, bg=self.colors['bg_dark'], highlightthickness=1,
                                 highlightbackground=self.colors['border'])
        text_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(text_container, height=15, width=70, 
                                                     state='disabled', wrap=tk.WORD,
                                                     bg=self.colors['bg_dark'],
                                                     fg=self.colors['fg'],
                                                     insertbackground=self.colors['fg'],
                                                     selectbackground=self.colors['accent_blue'],
                                                     relief='flat',
                                                     borderwidth=0,
                                                     font=('Consolas', 9),
                                                     padx=8, pady=8)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.status_text.tag_config('error', foreground='#ff5252')
        self.status_text.tag_config('success', foreground='#69f0ae')
        self.status_text.tag_config('warning', foreground='#ffd740')
        self.status_text.tag_config('info', foreground='#40c4ff')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status label
        self.status_label_var = tk.StringVar(value="Ready to scan")
        status_label = ttk.Label(main_frame, textvariable=self.status_label_var, 
                                font=('Helvetica', 11, 'bold'),
                                foreground=self.colors['accent_blue'])
        status_label.grid(row=5, column=0, columnspan=3, pady=(5, 0))
        
        # Make the status text area expandable
        main_frame.rowconfigure(3, weight=1)
        
    def log_status(self, message, tag=None):
        """Append message to status text widget."""
        self.status_text.configure(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        if tag:
            self.status_text.insert(tk.END, full_message, tag)
        else:
            self.status_text.insert(tk.END, full_message)
        
        self.status_text.see(tk.END)  # Auto-scroll to bottom
        self.status_text.configure(state='disabled')
        self.root.update_idletasks()
        
    def load_config(self):
        """Load last used configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Don't auto-load description to avoid accidental reuse
                    # but keep it available for "Use Last" button
                    self.last_config = config
                self.log_status("Configuration loaded", 'info')
        except Exception as e:
            self.log_status(f"Could not load config: {e}", 'warning')
            self.last_config = {}
            
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            config = {
                'description': self.description_var.get(),
                'year': self.year_var.get(),
                'last_photo': self.last_photo_var.get(),
                'cycles': self.cycles_var.get(),
                'port': self.port_var.get(),
                'timestamp': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_status("Configuration saved", 'info')
        except Exception as e:
            self.log_status(f"Could not save config: {e}", 'warning')
            
    def use_last_description(self):
        """Load the last description from log file."""
        last_photo_no, description, year = get_last_log_entry(self.log_file)
        
        if description:
            self.description_var.set(description)
            if year:
                # Year is already in 4-digit format (19XX), extract last 2 digits
                self.year_var.set(year[2:] if len(year) == 4 else year)
                self.log_status(f"Loaded last description: {description} ({year})", 'success')
            else:
                self.log_status(f"Loaded last description: {description}", 'success')
        else:
            self.log_status("No previous log entry found", 'warning')
            
    def continue_from_last(self):
        """Load the last photo number from log file and increment by 1."""
        last_photo_no, description, year = get_last_log_entry(self.log_file)
        
        if last_photo_no is not None:
            self.last_photo_var.set(str(last_photo_no))
            if description:
                self.description_var.set(description)
                if year:
                    # Year is already in 4-digit format (19XX), extract last 2 digits
                    self.year_var.set(year[2:] if len(year) == 4 else year)
            self.log_status(f"Continuing from photo #{last_photo_no}", 'success')
        else:
            self.log_status("No previous log entry found", 'warning')
            
    def validate_inputs(self):
        """Validate user inputs before starting scan."""
        try:
            cycles = int(self.cycles_var.get())
            if cycles <= 0:
                raise ValueError("Cycles must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Number of cycles must be a positive integer")
            return False
            
        try:
            last_photo = int(self.last_photo_var.get())
            if last_photo < 0:
                raise ValueError("Photo number cannot be negative")
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Last photo number must be a non-negative integer")
            return False
            
        description = self.description_var.get().strip()
        if not description:
            result = messagebox.askyesno("No Description", 
                                        "No description provided. Continue anyway?")
            if not result:
                return False
            self.description_var.set("No description")
        
        # Validate year (2 digits, optional)
        year_input = self.year_var.get().strip()
        if year_input:
            if not year_input.isdigit() or len(year_input) != 2:
                messagebox.showerror("Invalid Input", 
                                   "Year must be 2 digits (e.g., 85 for 1985)")
                return False
            
        return True
        
    def start_scan(self):
        """Start the scanning process in a separate thread."""
        if not self.validate_inputs():
            return
            
        # Save configuration
        self.save_config()
        
        # Disable start button, enable stop button
        self.start_btn.configure_state('disabled')
        self.stop_btn.configure_state('normal')
        self.scanning = True
        self.stop_requested = False
        
        # Clear status
        self.status_text.configure(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state='disabled')
        
        self.progress_var.set(0)
        self.status_label_var.set("Initializing scan...")
        
        # Start scan in separate thread to keep GUI responsive
        self.scan_thread = threading.Thread(target=self.run_scan, daemon=True)
        self.scan_thread.start()
        
    def emergency_stop(self):
        """Emergency stop - equivalent to Ctrl-C."""
        self.stop_requested = True
        self.log_status("EMERGENCY STOP REQUESTED!", 'error')
        self.status_label_var.set("Stopping...")
        
        # Try to disconnect gracefully if connected
        if self.marlin:
            try:
                self.log_status("Attempting graceful shutdown...", 'warning')
                DisconnectFromMarlin(self.marlin)
                self.marlin = None
            except Exception as e:
                self.log_status(f"Error during emergency stop: {e}", 'error')
    
    def emergency_home_x_axis(self):
        """Emergency function to return X-axis to home position."""
        try:
            # Get the current X position from user input
            current_position = float(self.x_position_var.get())
            
            # Validate position
            if current_position < 0 or current_position > MAX_X_TRAVEL:
                messagebox.showerror("Invalid Position", 
                                   f"Position must be between 0 and {MAX_X_TRAVEL}")
                return
            
            # Confirm action
            confirm = messagebox.askyesno("Confirm Emergency Home",
                                         f"This will move X-axis from position {current_position} to home (0).\\n\\n"
                                         f"Make sure the system is safe to move!\\n\\n"
                                         "Continue?")
            if not confirm:
                return
            
            self.log_status("=== EMERGENCY X-AXIS RETURN ===", 'warning')
            self.log_status(f"Current position: {current_position} rotations", 'info')
            
            # Connect to Marlin
            port = self.port_var.get().strip() or DEFAULT_PORT
            baudrate = DEFAULT_BAUD
            
            self.log_status(f"Connecting to Marlin on {port}...", 'info')
            temp_marlin = ConnectToMarlin(port, baudrate)
            self.log_status("Connected!", 'success')
            
            # Move to home position using relative positioning
            self.log_status(f"Moving X-axis -{current_position} rotations to home position (0)...", 'info')
            SendMarlinCmd(temp_marlin, "G91")  # Relative positioning
            # Move negative distance to return to home
            move_distance = -current_position
            SendMarlinCmd(temp_marlin, f"G0 X{move_distance} F{X_FEEDRATE}")
            SendMarlinCmd(temp_marlin, "M400")  # Wait for move to complete
            
            # Wait for movement to complete
            self.log_status("Waiting for movement to complete...", 'info')
            time.sleep(max(3, abs(move_distance) / 500))  # Scale wait time based on distance
            self.log_status("Waiting for movement to complete...", 'info')
            time.sleep(max(2, abs(move_distance) / 500))  # Scale wait time based on distance
            
            # Switch back to absolute positioning
            SendMarlinCmd(temp_marlin, "G90")
            
            self.log_status("X-axis returned to home position!", 'success')
            
            # Update the entry field
            self.x_position_var.set("0")
            
            # Disconnect
            DisconnectFromMarlin(temp_marlin)
            self.log_status("Disconnected from Marlin", 'info')
            
            messagebox.showinfo("Success", "X-axis has been returned to home position (0)")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for position")
        except Exception as e:
            error_msg = f"Emergency home failed: {e}"
            self.log_status(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
                
    def run_scan(self):
        """Main scanning routine - runs in separate thread."""
        try:
            # Get parameters
            port = self.port_var.get().strip() or DEFAULT_PORT
            baudrate = DEFAULT_BAUD
            distance = 2550  # millimeters per cycle
            STANDARD_FEED_RATE = 100000
            
            # Build full description with year in 4-digit format
            description = self.description_var.get().strip()
            year_input = self.year_var.get().strip()
            if year_input:
                description = f"{description} 19{year_input}"
            
            last_photo_no = int(self.last_photo_var.get())
            num_cycles = int(self.cycles_var.get())
            
            # Validate X-axis travel limits
            max_slides = MAX_X_TRAVEL // X_STEP_PER_SLIDE
            if num_cycles > max_slides:
                error_msg = (f"Requested {num_cycles} cycles exceeds maximum X-axis travel!\n"
                           f"Maximum slides available: {max_slides} (total travel: {MAX_X_TRAVEL}, "
                           f"step per slide: {X_STEP_PER_SLIDE})")
                self.log_status(error_msg, 'error')
                messagebox.showerror("X-axis Travel Error", error_msg)
                return
            
            # Calculate remaining X travel
            remaining_x_travel = MAX_X_TRAVEL - (num_cycles * X_STEP_PER_SLIDE)
            self.log_status(f"X-axis travel plan:", 'info')
            self.log_status(f"  Total available: {MAX_X_TRAVEL} rotations", 'info')
            self.log_status(f"  Required for {num_cycles} slides: {num_cycles * X_STEP_PER_SLIDE} rotations", 'info')
            self.log_status(f"  Remaining after completion: {remaining_x_travel} rotations", 'info')
            
            # Connect to Marlin
            self.log_status(f"Connecting to Marlin on {port}...", 'info')
            self.marlin = ConnectToMarlin(port, baudrate)
            self.log_status("Connected successfully!", 'success')
            
            if self.stop_requested:
                raise KeyboardInterrupt("Scan stopped by user")
            
            # Home Y axis
            self.status_label_var.set("Homing Y axis...")
            self.log_status("Homing Y axis...", 'info')
            home_y_axis(self.marlin)
            self.log_status("Y axis homed successfully", 'success')
            
            if self.stop_requested:
                raise KeyboardInterrupt("Scan stopped by user")
            
            # Initialize X-axis to starting position
            self.status_label_var.set("Initializing X-axis...")
            self.log_status(f"Moving X-axis to starting position (+{MAX_X_TRAVEL} rotations)...", 'info')
            SendMarlinCmd(self.marlin, "G90")  # Ensure absolute positioning
            MoveXAxis(self.marlin, MAX_X_TRAVEL, X_FEEDRATE)
            current_x_position = MAX_X_TRAVEL
            self.log_status(f"X-axis at position: {current_x_position}", 'success')
            
            if self.stop_requested:
                raise KeyboardInterrupt("Scan stopped by user")
            
            # Start movement cycles
            self.log_status(f"Starting {num_cycles} cycles of movement...", 'info')
            self.log_status(f"Each cycle: +{distance}mm, pause 0.5s, -{distance}mm", 'info')
            
            # Switch to relative positioning
            SendMarlinCmd(self.marlin, "G91")
            
            current_photo_no = last_photo_no
            
            for cycle in range(1, num_cycles + 1):
                if self.stop_requested:
                    raise KeyboardInterrupt("Scan stopped by user")
                
                # Update progress
                progress = (cycle - 1) / num_cycles * 100
                self.progress_var.set(progress)
                self.status_label_var.set(f"Cycle {cycle}/{num_cycles}")
                
                self.log_status(f"--- Cycle {cycle} of {num_cycles} ---", 'info')
                
                # Move in positive direction
                self.log_status(f"Moving +{distance}mm...")
                MoveFilm(self.marlin, distance, STANDARD_FEED_RATE)
                
                if self.stop_requested:
                    raise KeyboardInterrupt("Scan stopped by user")
                
                # Move X-axis backward for next slide (skip on first cycle)
                if cycle > 1:
                    self.log_status(f"Moving X-axis -{X_STEP_PER_SLIDE} rotations...")
                    # Temporarily switch to absolute positioning for X-axis
                    SendMarlinCmd(self.marlin, "G90")
                    current_x_position -= X_STEP_PER_SLIDE
                    MoveXAxis(self.marlin, current_x_position, X_FEEDRATE)
                    # Switch back to relative positioning for Y-axis cycles
                    SendMarlinCmd(self.marlin, "G91")
                    self.log_status(f"X-axis now at position: {current_x_position}", 'success')
                    self.log_status(f"Remaining X travel: {current_x_position} rotations", 'info')
                
                if self.stop_requested:
                    raise KeyboardInterrupt("Scan stopped by user")
                
                # Pause
                self.log_status("Pausing 0.5 seconds...")
                time.sleep(0.5)
                
                # Move in negative direction
                self.log_status(f"Moving -{distance}mm...")
                MoveFilm(self.marlin, -distance, STANDARD_FEED_RATE)
                
                if self.stop_requested:
                    raise KeyboardInterrupt("Scan stopped by user")
                
                self.log_status(f"Cycle {cycle} complete", 'success')
                
                # Take photo
                try:
                    current_photo_no += 1
                    take_photo(self.marlin, current_photo_no, description, self.log_file)
                    self.log_status(f"Photo #{current_photo_no} captured", 'success')
                except Exception as e:
                    self.log_status(f"Photo capture failed: {e}", 'error')
                
                # Run return sequence on final cycle
                if cycle == num_cycles:
                    try:
                        self.log_status("Running return sequence...")
                        return_last(self.marlin, distance, STANDARD_FEED_RATE)
                    except Exception as e:
                        self.log_status(f"Return sequence failed: {e}", 'error')
            
            # Return to absolute positioning
            SendMarlinCmd(self.marlin, "G90")
            
            # Return X-axis to home position (0)
            self.log_status("Returning X-axis to home position (0)...", 'info')
            MoveXAxis(self.marlin, 0, X_FEEDRATE)
            self.log_status("X-axis returned to home position", 'success')
            
            # Complete
            self.progress_var.set(100)
            self.status_label_var.set("Scan completed successfully!")
            self.log_status(f"All {num_cycles} cycles completed successfully!", 'success')
            
        except KeyboardInterrupt as e:
            self.log_status(f"Scan interrupted: {e}", 'error')
            self.status_label_var.set("Scan stopped by user")
            
        except Exception as e:
            self.log_status(f"ERROR: {e}", 'error')
            self.status_label_var.set("Scan failed - see errors above")
            messagebox.showerror("Scan Error", f"An error occurred:\n{e}")
            
        finally:
            # Always disconnect
            if self.marlin:
                try:
                    self.log_status("Disconnecting from Marlin...")
                    DisconnectFromMarlin(self.marlin)
                    self.log_status("Disconnected", 'info')
                except Exception as e:
                    self.log_status(f"Error during disconnect: {e}", 'error')
                finally:
                    self.marlin = None
            
            # Re-enable controls
            self.scanning = False
            self.start_btn.configure_state('normal')
            self.stop_btn.configure_state('disabled')
            
    def on_closing(self):
        """Handle window close event."""
        if self.scanning:
            result = messagebox.askyesno("Scan in Progress", 
                                        "A scan is currently running. Stop and exit?")
            if result:
                self.emergency_stop()
                # Give it a moment to stop
                self.root.after(1000, self.force_quit)
            return
        self.root.destroy()
        
    def force_quit(self):
        """Force quit the application."""
        try:
            if self.scan_thread and self.scan_thread.is_alive():
                # Thread cleanup
                pass
        except:
            pass
        self.root.destroy()


def main():
    """Main entry point for the GUI."""
    root = tk.Tk()
    app = ScannerGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
