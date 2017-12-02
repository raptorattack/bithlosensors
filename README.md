of# bithlosensors

-Raspberry Pi python script for reading/broadcasting sensor information, taking pictures, and feeding fish

-Arduino code for feeding fish and relaying the message of success to the Raspberry Pi main hub

///////////////////////////////////////////

UPDATE 12-1-17

The MQTT portion of the code is now fully functional and the system can operate up to two remote feeders at a time. Remote feeders should be plugged in first (since they only dispense food when the main hub says so). I have also added a layer of error prevention by pinging a website to check for a connection to the web before attempting to post to twitter. Photo brightness is boosted to 4.0 in attempt to optimize quality for dark lighting. A later software version may incorporate either infrared or visible LED lights on a relay if no ambient lights are added to the fish tanks.

///////////////////////////////////////////

UPDATE 9-24-17

I have uploaded the Arduino code for the first of two (identical) feeder nodes, the second of which will simply have a different ID. I have added communication via WiFi using MQTT to allow the nodes to notify the main hub that they have successfully fed the fish. The code is nearly complete as I have enabled communication but not yet added the "notify" feature implementation.

///////////////////////////////////////////


Tips for getting started:

-Twitter information is not included in the code, the keys and secrets are given upon setup of the Twitter account for your Pi

-The hour of day you would like the fish to be fed is specified by FEEDTIME in the top of the code (set 0-23)

-The amount of food given to the fish is decided in part by FEEDAMOUNT, it has not been tested yet for a reasonable value

-The time between Twitter updates is specified by SLEEP. This is in seconds (3600 is once per hour, not including time taken to execute code)

-The Adafruit stepper motor hat needs a 12V power source to power a 12V stepper motor if that's what you choose to use, suggest 1Amp or more

-I used crontab to have the Pi execute the script upon startup, there are tutorials for setup available online



Other notes:

-Images are resized to half original size for faster upload time over slow connections (and save Twitter server space :D)

-Images taken are uploaded and then deleted to save the Pi SD card space. The code to delete the photos is near the bottom and can be commented out

-I set the code to wait 1 minute before starting, to allow the Pi time to access a wifi connection if a saved connection is available

///////////////////////////////////////
