###   BITHLO AQUAPONICS SENSOR SYSTEM REV1.0   ###
###                                            ###
###   AUTHOR:   ADAM BROCKMEIER                ###
###   DATE:     11/15/2016                     ###
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
from time import strftime
from twython import Twython
from PIL import Image
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor


FEEDTIME = 12 #fish feeding time (military format, 0-23 o'clock)
FEEDAMOUNT = 2 #how long to leave the fish feeder open (in seconds)
SLEEP = 3600 #time between Twitter updates (in seconds)



#WAIT TO START UNTIL WIFI IS HOPEFULLY CONNECTED
time.sleep(60)
#WAIT TO START UNTIL WIFI IS HOPEFULLY CONNECTED

#INITIALIZE MOTOR
FED = 0 #assume fish have not been fed yet when starting program
mh = Adafruit_MotorHAT(addr = 0x60) #default address for the object is 0x60
myStepper = mh.getStepper(200,1) #200 steps/revolution, motor port #1
myStepper.setSpeed(1000) #motor speed, set around 1000 to be quick
#INITIALIZE MOTOR

#PULL TEMPERATURE READING FROM SENSOR
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
#PULL TEMPERATURE READING FROM SENSOR

#TWITTER ACCOUNT INFO
CONSUMER_KEY = '***' #add your twitter information from the twitter API setup
CONSUMER_SECRET = '***'
ACCESS_KEY = '***'
ACCESS_SECRET = '***'
#TWITTER ACCOUNT INFO

#SPECIFY THE NUMBER OF PHOTOS (999999999 or something to have a constant loop)
FRAMES = 999999999
TIMEBETWEEN = 6
#SPECIFY THE NUMBER OF PHOTOS

#LOOP (EVERYTHING INDENTED IS LOOPED)
frameCount = 0
while frameCount < FRAMES:

#SET THE TIME
    x = time.localtime(time.time()) #pulling the time of day for the next line
    HOUR = x.tm_hour #the current hour of day
#SET THE TIME

#RESET FISH FEEDER EACH MORNING
    if HOUR < FEEDTIME:
        FED = 0;
#RESET FISH FEEDER EACH MORNING

#FEED FISH
    if FED == 0 and HOUR >= FEEDTIME: #if fish haven't been fed and it's past feed time
        myStepper.step(200, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
        time.sleep(FEEDAMOUNT) #set in start of code
        myStepper.step(200, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
        FED = 1 #the fish have now been fed for the day
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
    #TURN ON INFRARED RING
    #TURN ON INFRARED RING
    imageNumber = str(frameCount).zfill(7)
    TIME = time.strftime("%m-%d-%Y--%H:%M:%S")
    DATE = time.strftime("%m/%d/%Y, %-I:%M%p")
    TEMP = read_temp()
    FILE = '%s_-_%sdegreesF'%(TIME,TEMP)
    os.system("raspistill -o /home/pi/Pictures/%s.jpg"%(FILE))
    frameCount += 1;
    time.sleep(TIMEBETWEEN - 6)
    #TURN OFF INFRARED RING
    #TURN OFF INFRARED RING
#CAPTURE PHOTO

#RESIZE PHOTO
    photo = Image.open('/home/pi/Pictures/%s.jpg'%(FILE))
    # Twitter displays images at 440px width
    Width = 1760
    # Calculate size difference between original and 440px
    width_percent = (Width/float(photo.size[0]))
    # Use that percentage to determine the new height to resize
    Height = int((float(photo.size[1])*float(width_percent)))
    # Resize image to optimal Twitter size
    photo = photo.resize((Width,Height), Image.BILINEAR)
    # Resize image
    photo.save("/home/pi/Pictures/%s.jpg"%(FILE))
#RESIZE PHOTO

#UPLOAD PHOTO
    photo = open('/home/pi/Pictures/%s.jpg'%(FILE))
    twitter = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET)
    image = twitter.update_status_with_media(media=photo)
    if FED == 0:
        twitter.update_status(status="Time: %s\nWater Temperature: %s*F\nFish Fed: No"%(DATE,TEMP))
    if FED == 1:
        twitter.update_status(status="Time: %s\nWater Temperature: %s*F\nFish Fed: Yes"%(DATE,TEMP))
#UPLOAD PHOTO

#DELETE FILES ONCE THEY ARE UPLOADED
    directory = '/home/pi/Pictures'
    os.chdir(directory)

    files = glob.glob('%s.jpg'%(FILE))

    numfiles = next(os.walk(directory))[2]

    if len(numfiles) > 0:
        for filename in files:
            os.unlink(filename)
#DELETE FILES ONCE THEY ARE UPLOADED

#DELAY UNTIL NEXT PHOTO
    time.sleep(SLEEP) #set in start of code
#DELAY UNTIL NEXT PHOTO

#END OF LOOP



raise SystemExit
