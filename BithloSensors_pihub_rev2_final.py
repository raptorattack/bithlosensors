###   BITHLO AQUAPONICS SENSOR SYSTEM REV2.0   ###
###                                            ###
###   AUTHOR:   ADAM BROCKMEIER                ###
###   DATE:     12/1/2017                      ###
###   CONTACT:  brockmeier.adam@gmail.com      ###
###                                            ###
###   THIS CODE WAS DEVELOPED TO MAINTAIN      ###
###   (AND BROADCAST INFORMATION ABOUT) THE    ###
###   AQUAPONICS SYSTEM IN BITHLO, FLORIDA,    ###
###   DEVELOPED BY THE ENGINEERS WITHOUT       ###
###   BORDERS CLUB AT UCF.                     ###
###                                            ###
###   IT READS CURRENT WATER TEMPERATURE,      ### 
###   TAKES PHOTOS, AND FEEDS FISH ON          ###
###   A DAILY BASIS AT A SPECIFIED TIME.       ###
###                                            ###
###   INFORMATION IS TWEETED TO THE            ###
###   @BithloAquaponic TWITTER ACCOUNT.        ###

import os
import time
import glob
import sys
import socket
from time import strftime
from twython import Twython
from PIL import Image, ImageEnhance
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import paho.mqtt.client as mqtt


#WAIT TO START UNTIL WIFI IS HOPEFULLY CONNECTED
time.sleep(60)
#WAIT TO START UNTIL WIFI IS HOPEFULLY CONNECTED

#INITIALIZE
global Node1Fed
mh = Adafruit_MotorHAT(addr = 0x60) #default address for the object is 0x60
myStepper = mh.getStepper(200,1) #200 steps/revolution, motor port #1
myStepper.setSpeed(1000) #motor speed, set around 1000 to be quick
#INITIALIZE

#DEFINE MESSAGES RECEIVED BY NODES
def on_connect (client, userdata, flags, rc):
    client.subscribe("EWBAqua_Node2")
    client.subscribe("EWBAqua_Node3")
def on_message (client, userdata, msg):
    global Node2Fed
    global Node3Fed
    Node2Fed = "No"
    Node3Fed = "No"
    if (str(msg.topic) == "EWBAqua_Node2"):
        Node2Fed = str(msg.payload)
    if (str(msg.topic) == "EWBAqua_Node3"):
        Node3Fed = str(msg.payload)
#DEFINE MESSAGES RECEIVED BY NODES

#CONNECT TO LOCAL BROKER
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#CONNECT TO LOCAL BROKER
        
#PULL TEMPERATURE READING FROM SENSOR
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm') 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
#PULL TEMPERATURE READING FROM SENSOR

#TWITTER ACCOUNT INFO
CONSUMER_KEY = 'Redacted'
CONSUMER_SECRET = 'Redacted'
ACCESS_KEY = 'Redacted'
ACCESS_SECRET = 'Redacted'
#TWITTER ACCOUNT INFO

#SET FOCUS TIME OF CAMERA
TIMEBETWEEN = 6
#SET FOCUS TIME OF CAMERA

#LOOP (EVERYTHING INDENTED IS LOOPED)
frameCount = 0
while True:

#SET THE TIME
    x = time.localtime(time.time()) #pulling the time of day for the next line
    HOUR = x.tm_hour #the current hour of day
#SET THE TIME

#FEED FISH
    Node1Fed = "NA" #Will display "not available" if feeding is unsuccessful
    client.connect('localhost',1883,60)
    #print("client just connected, About to feed node1")
    client.publish("EWBAqua_Node_Feedsignal","FeedNow\0")
    client.loop_start()
    myStepper.step(220, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE)
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    Node1Fed = "Yes"
    time.sleep(3)
    client.loop_stop()
    client.publish("EWBAqua_Node_Feedsignal","NotFeedTime\0")
#FEED FISH
    
#PULL TEMPERATURE READING FROM SENSOR
    def read_temp_raw():
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
     
    def read_temp():
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_f
#PULL TEMPERATURE READING FROM SENSOR

#CAPTURE PHOTO
    imageNumber = str(frameCount).zfill(7)
    TIME = time.strftime("%m-%d-%Y--%H:%M:%S")
    DATE = time.strftime("%m/%d/%Y, %-I:%M%p")
    TEMP = read_temp()
    FILE = '%s_-_%sdegreesF'%(TIME,TEMP)
    os.system("raspistill -o /home/pi/Pictures/%s.jpg"%(FILE))
    frameCount += 1;
    time.sleep(TIMEBETWEEN - 6)
#CAPTURE PHOTO

#RESIZE PHOTO
    photo = Image.open('/home/pi/Pictures/%s.jpg'%(FILE))
    # Twitter displays images at 440px width
    Width = 1920
    # Calculate size difference between original and 440px
    width_percent = (Width/float(photo.size[0]))
    # Use that percentage to determine the new height to resize
    Height = int((float(photo.size[1])*float(width_percent)))
    # Resize image to optimal Twitter size
    photo = photo.resize((Width,Height), Image.BILINEAR)
    # Resize image
    enhancer = ImageEnhance.Brightness( photo )
    photo = enhancer.enhance( 4.0 )
    # Increase brightness
    photo.save("/home/pi/Pictures/%s.jpg"%(FILE))
#RESIZE PHOTO

#UPLOAD PHOTO
    network_err = 0
    try:
        socket.gethostbyname('www.google.com')
    except socket.gaierror:
        network_err = 1
    if network_err == 0:
        photo = open('/home/pi/Pictures/%s.jpg'%(FILE))
        twitter = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET)
        image = twitter.update_status_with_media(media=photo)
        twitter.update_status(status="Time: %s\nWater Temp.: %s*F\nTank 1 Fed: %s\nTank 2 Fed: %s\nTank 3 Fed: %s"%(DATE,TEMP,Node1Fed,Node2Fed,Node3Fed))
#UPLOAD PHOTO

#DELETE FILES WHEN THEY ARE UPLOADED
    directory = '/home/pi/Pictures'
    os.chdir(directory)

    files = glob.glob('%s.jpg'%(FILE))

    numfiles = next(os.walk(directory))[2]

    if len(numfiles) > 0:
        for filename in files:
            os.unlink(filename)
#DELETE FILES AFTER THEY ARE UPLOADED

#DELAY UNTIL NEXT FEEDING
    time.sleep(302380) #seconds, feeding twice a week
#DELAY UNTIL NEXT FEEDING

#END OF LOOP

raise SystemExit
