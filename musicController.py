#Music Controller - Zachary del Rosario 12/16/2013
#This script is intended to run on a Raspberry Pi, take input from four ultrasonic rangefinders through a 4-to-1 multiplexer, and output data through a system-message to a Pure Data patch.

#Import requisite modules
import serial, time, RPi.GPIO as io, os
#Initialize serial port
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.01)
ser.open()
#Initialize timer, used for manual serial timeout and channel switching
time0 = time.clock()
inter = 0.02
#Initialize GPIO pins
io.setmode(io.BCM)
pinA = 18 #assign control pin A
pinB = 23 #assign control pin B
valA = False   #control logic value
valB = False
io.setup(pinA, io.OUT) #initialize for output
io.setup(pinB, io.OUT) #initialize for output
io.output(pinA, valA) #set initial pin value
io.output(pinB, valB)
#Initialize string buffer
buf = ''
num = 0
#Initialize control variables
channel = 0 #channel value
ch_num = 4 #number of channels (max 4)
state = 0 #reading state: 0 awaiting read start, 1 reading, 2 awaiting send
dist = [1,1,1,1] #list of distances from channels
hof = 40 #highest (midi) frequency allowed

#channel map: returns a boolean tuple to switch the multiplexer control pins, based on a base-10 channel number
def channel_map(num):
    return {
        0: [False,False],
        1: [False,True],
        2: [True,False],
        3: [True,True],
    }.get(num, [False,False])
#send a system message to Pure Data, this allows python to send information to Pd
def send2Pd(message=''):
    # Send a message to Pd
    # note, this will throw a 'connect: Connection refused (111)' error
    #  if Pd is not running
    os.system("echo '" + message + "' | pdsend 3000")
#build a string message out of a list, used to properly format the Pd message
def build_message(L):
    s0 = str(L[0])
    s1 = str(L[1])
    s2 = str(L[2])
    s3 = str(L[3])
    return  s0+' '+s1+' '+s2+' '+s3+';' #string must terminate in a semicolon in order to send properly

#sent a start message to Pd to set the idle values
send2Pd('1 1 1 1;')
#start the reactor!
print "Start"

#try block allows keyboard interrupt to end loop cleanly
try:
    # MAIN LOOP
    while 1:
        #read serial data
        char_out = ser.read()
        # READ PACKET HEADER
        if char_out == 'R': #'R' signals a new packet
            # print buf
            # BEGIN READ
            if state == 0:
                #begin read
                state = 1
            # SEND MESSAGE
            elif state == 1:
                try:
                    # BUILD MESSAGE
                    num = min(hof,int(buf)) #convert buffer contents to integer
                    if num > 55: #catch bugged out numbers
                        num = 1
                    dist[channel] = num #store distance in appropriate slot
                    message = build_message(dist)
                    print message
                    send2Pd(message)
                    # SWITCH CHANNEL
                    time0 = time.clock() #reset timeout
                    state = 0 #set to await next read
                    channel = (channel + 1) % ch_num #cycle the channel number
                    buf = '' # clear the buffer
                    # print 'channel: '+str(channel) #print the channel number
                    (valA, valB) = channel_map(channel) #set mux control pins
                    # print valB, valA
                    io.output(pinA, valA) #write the value to the pin
                    io.output(pinB, valB)
                #catch non-integer characters
                except ValueError:
                    num = 1 #catch bad characters, default to 0 value
                    state = 0 #reset and just wait for the next start character
                    buf = ''
            
        # READ DIGIT
        elif (char_out in '0123456789') and (state == 1):
            buf = buf + char_out #add character to buffer
        
        #TIMEOUT CLOCK
        newTime = time.clock()
        if (time.clock() - time0) > inter:
            # SWITCH CHANNEL
            time0 = newTime #reset timeout
            state = 0 #set to await next read
            channel = (channel + 1) % ch_num #cycle the channel number
            buf = '' # clear the buffer
            # print 'channel: '+str(channel) #print the channel number
            (valA, valB) = channel_map(channel) #set mux control pins
            # print valB, valA
            io.output(pinA, valA) #write the value to the pin
            io.output(pinB, valB)
            print 'TIMEOUT'
#Catch a keyboard interrupt to clean up the pins - this prevents error on running the script again
except KeyboardInterrupt:
    ser.close()
    io.cleanup()
    send2Pd('0 0 0 0;')
    print "Serial connection terminated"


