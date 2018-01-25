#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import os
import sys
import glob
import subprocess
#from subprocess import Popen
from gpiozero import MotionSensor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
omxc = ''

#Set GPIO for the PIA
PIR_PIN = 7
pir = MotionSensor(PIR_PIN)

#List of pin nimbers
#pinList = [4, 17, 27, 22, 10, 9, 11, 5] # this is a list for all 8 relays 
pinList = [4, 17, 27]

# Setup relay pins
for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
#    print ('GPIO Pin number ', i)

player = False


# ++++++++++++++++++++++++ End of global setup ++++++++++++++++++++
#####################################################
# Set relays for different lighting
#####################################################    
def setLights(stage):
    global omxc

    if stage == 1:
        # Enter the C130
        GPIO.output(pinList[0], GPIO.HIGH)  #white lights on
        GPIO.output(pinList[1], GPIO.HIGH)  #green lights off
        GPIO.output(pinList[2], GPIO.HIGH)  #exit sign off

    elif stage == 2:
        # Watch the pressentation
        GPIO.output(pinList[0], GPIO.LOW)  # white lights off
        GPIO.output(pinList[1], GPIO.LOW)  # green lights on
        GPIO.output(pinList[2], GPIO.HIGH) # exit sign off
    else:
        # Exit the C130
        GPIO.output(pinList[0], GPIO.LOW)  # white lights off
        GPIO.output(pinList[1], GPIO.LOW)  # green lights on
        GPIO.output(pinList[2], GPIO.LOW)  # exit sign on


#####################################################        
# Find the path to the USB pen
#####################################################    
def usbPath():
    pathToUsb = ''
    
    output = subprocess.Popen("lsblk", stdout=subprocess.PIPE, shell=True)
    for out in output.communicate()[0].split():
      #  print ("out is " , out)
        if bytes('/media/', 'utf-8') in out:
            pathToUsb = str(out, 'utf-8')
         #   print ("media found? " , pathToUsb)
    return  pathToUsb

#####################################################       
# Callback for the motion sensor event
#####################################################    
def MOTION(PIR_PIN):
    global player
    global pinList
    global GPIO
    global movie2
    global movie3
    global omxc

    # stop the first movie
    os.system('pkill omxplayer.bin')
   # White out & Green On
    setLights(2) # This is green lights
    omxc = subprocess.Popen(['omxplayer', '-b', '--no-osd','--no-keys', '-o','hdmi', movie2 ])
    omxc_status = omxc.wait() # wait for the pressentation to finish
  #  print ("Playing Movie 2 ", player)
 
   # Green on & Exit 0n
    setLights(3) # This is green with exit lights
    omxc = subprocess.Popen(['omxplayer','--no-osd', '-b', '--no-keys', '-o','hdmi', movie3 ])
    omxc_status = omxc.wait() # wait for the pressentation to finish
 #   print ("Playing Movie 3 ", player)
            

   # Green out & White On
    setLights(1) # This is white lights
  #  print ("Playing Movie 1 ", player)
    # Start the first movie 
    omxc = subprocess.Popen(['omxplayer', '--no-keys', '-b', '--loop', '--no-osd', '-o','hdmi', movie1])
    time.sleep(2) # allow time for the omxplayer to register with a PID
   # print ('restarted movie1')


#+++++++++++++++++++ Start of main file ++++++++++++++++
time.sleep(30)
theusbpath = usbPath()

# Find the mp4 file
movie1 =  theusbpath + '/first.mp4'
movie2 = theusbpath + '/main.mp4' 
movie3 = theusbpath + '/last.mp4' 

try:
    os.system('tvservice -o') #this will blank the screen
    os.system('tvservice -p') #this is part of the blank screen line above
#    print 'In main body of the program'

    setLights(1) # This is white lights
    omxc = subprocess.Popen(['omxplayer', '--no-keys', '-b',  '--loop', '--no-osd', '-o','hdmi', movie1])
    time.sleep(2) # wait befor allowing PIR interrupt

    while 1:
        if pir.motion_detected:
            MOTION(PIR_PIN)

        
except KeyboardInterrupt:
#    print (" Quit")
    GPIO.cleanup()
    
