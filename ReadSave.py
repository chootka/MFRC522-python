#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import os, time

os.system('echo none > /sys/class/leds/led0/trigger')
os.system('echo 0 > /sys/class/leds/led0/brightness')

mugs_filename = 'mugs_uids_' + time.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

store_uid = []

# This loop keeps checking for chips. If one is near it will get the UID
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # Read all 16 pages of Ultralight card
        try:
            (block, data) = MIFAREReader.MFRC522_Read(256)

            # Pull out the UID
 	        uid_dec = data[0:3] + data[4:8]
        except:
	        print 'reader error'

        # Convert to Hex
        uid = []
        for d in uid_dec:
            h = format(d, 'x')
            # Zero pad if single digit number
	        if len(str(h)) < 2:
	            h = '0' + str(h)
                uid.append(h)

        # Prevents multiple readings of same UID
	    if store_uid != uid:
            uid_str = ('').join(uid)
	        print uid_str

        # Flash ON the on-board green LED
	    os.system('echo 1 > /sys/class/leds/led0/brightness')

        # Write UID to output file
	    with open(mugs_filename, 'a') as the_file:
		    the_file.write(uid_str + '\n')
	        os.system('sync')
	        print (':').join(uid)
	        store_uid = uid
        # Flash OFF the on-board green LED after 1 second delay
	    time.sleep(1)
	    os.system('echo 0 > /sys/class/leds/led0/brightness')

