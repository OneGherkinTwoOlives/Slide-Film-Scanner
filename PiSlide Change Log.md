



**PiSlide1\_LinLong.py**

Dec 27, 2025



\*\*REQUEST\*\*

Can you remove unused libraries from the setup section of this code?





\*\*RESPONSE\*\*

Now I'll analyze which libraries are used and remove the unused ones:



queue: UNUSED (declared but not used)

Thread from threading: UNUSED (imported but never used)

Fraction from fractions: UNUSED

numpy (as np): UNUSED

os: UNUSED

serial: USED (for Serial class and constants)

math: UNUSED

datetime, timedelta: USED (in MarlinWaitForReply)

time: USED (for sleep and time.time())

sys: UNUSED

importlib: UNUSED

Edited

PiSlide1\_Lin.py+0-0

Removed unused libraries: queue, threading.Thread, fractions.Fraction, numpy, os, math, sys, and importlib. Also removed the unused NUM\_THREADS variable and q queue object.



The code now only imports what it actually uses: serial, datetime/timedelta, and time.





\*\*REQUEST\*\*

Okay, now I would like to add a function that records a log of the photos taken. This will function as follows:



Upon running, user input: "Provide Description (year, place, etc.)"? Create a new variable called "description"

Second input: "What is the last picture number?". Create a new variable called "last\_photo\_no." and each time take\_photo() runs, +1 to this value.

Then create a log.txt file in the same folder the working file is stored, If a log file already exists, use this and continue adding new lines to the bottom.

each time take\_photo() runs, record a new line in the log file with the current photo number (i.e. last\_photo\_no + the number of photos taken since), and the descriptiion.





\*\*RESPONSE\*\*

Done! The logging functionality has been added:



Description input: Prompts "Provide Description (year, place, etc.)" and stores it in the description variable

Starting photo number: Prompts "What is the last picture number?" and stores it in last\_photo\_no

Log file: Creates/appends to log.txt in the same folder as the script

Photo tracking: Each time take\_photo() runs, it increments the photo number and writes a new line to the log file in the format: Photo #\[number]: \[description]

The log file will be created automatically on the first run, and subsequent runs will append new entries to the existing file.









**PiSlide1\_LinLong2.py**

\*\*REQUEST\*\*

Now in this version, I want to change the behaviour of the log file function specifically when a log file already exists.



when a log.txt file already exists, the program should retrieve the last line of the file and prompt the user if it wants to continue from the last entry (i.e. using the last photo number and the description). The prompt would be: "Continue from: (photo number and description \[y/n])?

If the response is "y" or "yes" or enter, then the program uses the last photo number and description from the file, and skips the user input for description and last\_photo\_no\_input.

if the response is "n" or "no", then the script continues to the typical process for collecting the user input for description and last\_photo\_no\_input.

Edited





\*\*RESPONSE\*\*

PiSlide1\_LinLog2.py+0-0

Done! The log file functionality has been updated:



Existing log detection: When log.txt exists, the program reads and parses the last entry

Continue prompt: Shows "Continue from: Photo #\[number] - \[description] \[y/n]?"

Auto-continue: If user responds with "y", "yes", or just presses Enter, it uses the last photo number and description, skipping the input prompts

Fresh start: If user responds with "n" or "no", it proceeds with the normal user input prompts for description and last photo number

The get\_last\_log\_entry() function handles parsing the log file format and returns the photo number and description from the last entry.





