of# bithlosensors
Raspberry Pi python script for reading/broadcasting sensor information, taking pictures, and feeding fish



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
