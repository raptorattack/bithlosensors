// EWB Arduino Feeder Code Rev0.3
// Created By:   Adam Brockmeier
// Edit Date:    1-13-2018
//
// NODE 2
//
// Description: Arduino-based code for feeding the fish in the Bithlo Aquaponics
// system. Runs on WiFi and uses MQTT protocol to communicate to the main hub
// that its processes have been completed successfully.

#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <EEPROM.h>
#include "WEMOS_Motor.h"




//GLOBAL Variables
//Wifi and MQTT Credentials:
const char* ssid     = "EWBAquaponics";
const char* password = "3ngineertheFuture";
const char* mqtt_server = "192.168.1.125";
const char* mqtt_topic_pub = "EWBAqua_Node2";
const char* mqtt_topic_sub = "EWBAqua_Node_Feedsignal_2";
const char* clientID = "Node2";
int Fedstate = 0;

//Motor initialization:
Motor M1(0x30,_MOTOR_A, 200);//Motor A
Motor M2(0x30,_MOTOR_B, 200);//Motor B


//Motor spin loop settings:
const int i = 100; //duty cycle %
const int dlay = 2; //2ms between steps
int j;


//Callback function
void callback(char* topic, byte* payload, unsigned int length) {
 char* mqtt_topic_pub = "EWBAqua_Node2";
 WiFiClient espClient;
 PubSubClient client(mqtt_server, 1883, callback, espClient);
  
  char *cstring = (char *) payload;
  Serial.print(cstring);
  Serial.print("\n");
  if (strcmp(cstring, "FeedNow2") == 0)
  //if (i != 100)
  {
    //            ***SET THE FEEDING PART HERE***               //
    Fedstate = 1;
    Serial.println("was just told to feed");
    j = 200;
    while (j>0)
    {
      M2.setmotor(_CW, i); //CW facing the shaft
      delay(dlay);
      M1.setmotor(_CCW, i);
      delay(dlay);
      M2.setmotor(_CCW, i);
      delay(dlay);
      M1.setmotor(_CW, i);
      delay(dlay);
      j--;
    }
    M2.setmotor(_STANDBY);
    M1.setmotor(_STANDBY);
  }
}


WiFiClient espClient;
PubSubClient client(mqtt_server, 1883, callback, espClient);

//Reconnect to MQTT function
int reconnect_tries = 0;
void reconnect() {
PubSubClient client(mqtt_server, 1883, callback, espClient);
 // Loop until we're reconnected
 while (!client.connected() && reconnect_tries < 20) {

 Serial.print("Attempting MQTT connection...");
 // Attempt to connect
 if (client.connect("espClient")) {
  Serial.println("connected");
 } 
 else {
  Serial.print("failed, rc=");
  Serial.print(client.state());
  reconnect_tries++;
  Serial.println(" try again in 5 seconds");
    digitalWrite(BUILTIN_LED, HIGH);  // turn on LED with voltage HIGH
    delay(200);                      // wait one second
    digitalWrite(BUILTIN_LED, LOW);   // turn off LED with voltage LOW
    delay(200);                      // wait one second
    digitalWrite(BUILTIN_LED, HIGH);  // turn on LED with voltage HIGH
    delay(200);                      // wait one second
    digitalWrite(BUILTIN_LED, LOW);   // turn off LED with voltage LOW
    delay(200);                      // wait one second
    digitalWrite(BUILTIN_LED, HIGH);  // turn on LED with voltage HIGH
    delay(200);                      // wait one second
    digitalWrite(BUILTIN_LED, LOW);   // turn off LED with voltage LOW
    delay(200);                      // wait one second
  // Wait 4 seconds before retrying
  delay(4000);
  }
  client.subscribe(mqtt_topic_sub);
 }
}

//Wifi initialization function:
void wifi_initialize(){
  WiFi.begin(ssid, password); //begin wifi connection
  int wifi_tries = 0;
  while (WiFi.status() != WL_CONNECTED && wifi_tries < 20) { //try for 12 seconds to connect to wifi
    Serial.println("Wifi not connected");
    digitalWrite(BUILTIN_LED, HIGH);  // turn on LED with voltage HIGH
    delay(100);                      // wait one second
    digitalWrite(BUILTIN_LED, LOW);   // turn off LED with voltage LOW
    delay(100);                      // wait one second
    digitalWrite(BUILTIN_LED, HIGH);  // turn on LED with voltage HIGH
    delay(100);                      // wait one second
    digitalWrite(BUILTIN_LED, LOW);   // turn off LED with voltage LOW
    delay(100);                      // wait one second
    digitalWrite(BUILTIN_LED, HIGH);  // turn on LED with voltage HIGH
    delay(100);                      // wait one second
    digitalWrite(BUILTIN_LED, LOW);   // turn off LED with voltage LOW
    delay(100);                      // wait one second
    wifi_tries++;
  }
}



void setup() {
  pinMode(BUILTIN_LED, OUTPUT);  // initialize onboard LED as output
  Serial.begin(115200);
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  wifi_initialize();
  }



void loop() {
  if (!client.connected()) {
    reconnect();
  }
 client.loop();
 
 if (Fedstate != 0)
 {
    Serial.print("back in the main loop now\n");
    client.publish(mqtt_topic_pub, "Yes");
    Serial.println("just set the topic");
    delay(10000);
    client.publish(mqtt_topic_pub, "No");
    Serial.println("just cleared the topic\n");
    Fedstate = 0;
 }
}

///////////////////////////////END/////////////////////////////////
