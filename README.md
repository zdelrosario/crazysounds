crazysounds
===========
This is the code I developed as part of Computer Music at Wellesley College. The project was aimed at creating an interactive sound installation using a Raspberry Pi and four ultrasonic range finders. I had time to work out the engineering parts of the system, but not much of the sound design; thus the system collects data well, but doesn't make crazy enough sounds.

Files
===========
- musicController.py: python script which takes input from ultrasonic range finders and sends data to Pure Data patch
- python_receive.pd: Pure Data patch which receives data from python and outputs crazy sounds via the 1/8" jack
