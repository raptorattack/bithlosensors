###   BITHLO AQUAPONICS SENSOR SYSTEM REV2.1   ###
###                                            ###
###   AUTHOR:   ADAM BROCKMEIER                ###
###   DATE:     12/08/2019                     ###
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
###   A SEMI-WEEKLY BASIS.                     ###
###                                            ###
###   INFORMATION IS TWEETED TO THE            ###
###   @BithloAquaponic TWITTER ACCOUNT.        ###

import os
import time
import glob
import sys
import socket
import schedule
import time
from time import strftime
from twython import Twython
from PIL import Image
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import paho.mqtt.client as mqtt





#SET DAYS BETWEEN FEEDING
DAYSBETWEENFOOD = 3.5
#SET DAYS BETWEEN FEEDING





#WAIT TO START UNTIL WIFI IS HOPEFULLY CONNECTED
#ALSO AVOIDS OVERFEEDING FROM REPEATED POWER OUTAGES IN A SHORT TIME
#time.sleep(60)
#WAIT TO START UNTIL WIFI IS HOPEFULLY CONNECTED

#INITIALIZE MOTOR
mh = Adafruit_MotorHAT(addr = 0x60) #default address for the object is 0x60
myStepper = mh.getStepper(200,1) #200 steps/revolution, motor port #1
myStepper.setSpeed(1000) #motor speed, set around 1000 to be quick
#INITIALIZE MOTOR

#INITIALIZE TEMPERATURE SENSOR
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm') 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
#INITIALIZE TEMPERATURE SENSOR

#INITIALIZE CAMERA
FOCUSTIME = 6
FRAMECOUNT = 0
#INITIALIZE CAMERA

#SUBSCRIBE TO NODES
def on_connect (client, userdata, flags, rc):
    client.subscribe("EWBAqua_Node2")
    time.sleep(3)
    client.subscribe("EWBAqua_Node3")
#SUBSCRIBE TO NODES

#TWITTER ACCOUNT INFO
CONSUMER_KEY = 'KYMnNfNKypFtqGDsGodOsEhVw'
CONSUMER_SECRET = 'yWno5dgZsAnnuNKDBd3zYnXcR7wEkauiITjl9DNIs4l8lf6CP3'
ACCESS_KEY = '797467713597743104-1pVM7cFnKTblu1i0IaWiROKIrJ4QZhO'
ACCESS_SECRET = 'NBrExIPu8WdatS0sG3qiISHptiUqOS9yH1dPbtOKafGeY'
twitter = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET)
#TWITTER ACCOUNT INFO

#POST TO TWITTER IF ANY NODES GIVE AN UPDATE
def on_message (client, userdata, msg):
    if (str(msg.topic) == "EWBAqua_Node2"):
        #print("got a message from 2")
        global Node2Fed
        Node2Fed = str(msg.payload)
        DATE = time.strftime("%m/%d/%Y, %-I:%M%p")
        network_err = 0
        try:
            socket.gethostbyname('www.google.com')
        except socket.gaierror:
            network_err = 1
            #print ("not posting because no network\n")
        if network_err == 0:
            twitter.update_status(status="Time: %s\nTank 2 has been fed"%(DATE))
       
    if (str(msg.topic) == "EWBAqua_Node3"):
        #print("got a message from 3")
        global Node3Fed
        Node3Fed = str(msg.payload)
        DATE = time.strftime("%m/%d/%Y, %-I:%M%p")
        network_err = 0
        try:
            socket.gethostbyname('www.google.com')
        except socket.gaierror:
            network_err = 1
            #print ("not posting because no network\n")
        if network_err == 0:
            twitter.update_status(status="Time: %s\nTank 3 has been fed"%(DATE))
#POST TO TWITTER IF ANY NODES GIVE AN UPDATE

#CONNECT TO LOCAL BROKER
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost',1883,60)
client.loop_start()
#CONNECT TO LOCAL BROKER





#TURN MOTOR TO FEED FISH
def motor_run():
    myStepper.step(220, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE) #need to make the run time into a variable that can be set at the top of program
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
#TURN MOTOR TO FEED FISH

#READ TEMPERATURE FROM WATER SENSOR
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
#READ TEMPERATURE FROM WATER SENSOR

#CAPTURE A PHOTO
def capture_photo(FILE,DATE):
    global FRAMECOUNT
    #TURN ON INFRARED RING
    #TURN ON INFRARED RING
    imageNumber = str(FRAMECOUNT).zfill(7)
    #TIME = time.strftime("%m-%d-%Y--%H:%M:%S")
    #DATE = time.strftime("%m/%d/%Y, %-I:%M%p")
    os.system("raspistill -o /home/pi/Pictures/%s.jpg"%(FILE))
    FRAMECOUNT += 1;
    time.sleep(FOCUSTIME)
    return FILE
    #TURN OFF INFRARED RING
    #TURN OFF INFRARED RING
#CAPTURE A PHOTO

#RESIZE PHOTO
def resize_photo(FILE,DATE):
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

#UPLOAD PHOTO TO TWITTER
def upload_photo(FILE,DATE):
    network_err = 0
    try:
        socket.gethostbyname('www.google.com')
    except socket.gaierror:
        network_err = 1
        #print ("not posting because no network\n")
    if network_err == 0:
        photo = open('/home/pi/Pictures/%s.jpg'%(FILE))
        image = twitter.update_status_with_media(media=photo)
        TEMP = read_temp()
        twitter.update_status(status="Time: %s\nTank 1 has been fed\nWater Temp.: %s*F"%(DATE,round(TEMP,2)))
#UPLOAD PHOTO TO TWITTER

#DELETE FILES WHEN THEY ARE UPLOADED
def delete_photo(FILE,DATE):
    directory = '/home/pi/Pictures'
    os.chdir(directory)
    files = glob.glob('%s.jpg'%(FILE))
    numfiles = next(os.walk(directory))[2]
    if len(numfiles) > 0:
        for filename in files:
            os.unlink(filename)
#DELETE FILES AFTER THEY ARE UPLOADED

#FEEDING SEQUENCE
def feeding_sequence():
    motor_run()
    TEMP = read_temp()
    TIME = time.strftime("%m-%d-%Y--%H:%M:%S")
    FILE = '%s_-_pic_capture'%(TIME)
    DATE = time.strftime("%m/%d/%Y, %-I:%M%p")
    capture_photo(FILE,DATE)
    resize_photo(FILE,DATE)
    upload_photo(FILE,DATE)
    delete_photo(FILE,DATE)
#FEEDING SEQUENCE

#SCHEDULE THE FEEDING SEQUENCE
schedule.every(DAYSBETWEENFOOD).days.do(feeding_sequence) #substitute .days. for .minutes. if you want to test stuff quickly
#SCHEDULE THE FEEDING SEQUENCE

#RUN THE FEEDING SEQUENCE WHEN FIRST BOOTING
feeding_sequence()
#RUN THE FEEDING SEQUENCE WHEN FIRST BOOTING



#LOOP
while True:
    #FEEDING SEQUENCE WILL RUN EVERY X DAYS
    schedule.run_pending()
    time.sleep(2)
    #FEEDING SEQUENCE WILL RUN EVERY X DAYS
#LOOP





raise SystemExit
