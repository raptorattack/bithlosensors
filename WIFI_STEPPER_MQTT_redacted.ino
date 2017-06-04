#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <EEPROM.h>
#include "WEMOS_Motor.h"

//Motor initialization:
Motor M1(0x30,_MOTOR_A, 200);//Motor A
Motor M2(0x30,_MOTOR_B, 200);//Motor B


//Wifi and MQTT Credentials:
const char* ssid     = "wifinamehere";
const char* password = "wifipasswordhere";
const char* mqtt_server = "EWBAquaponics";
WiFiClient espClient;
PubSubClient client(espClient);

//Callback function
void callback(char* topic, byte* payload, unsigned int length) {
 Serial.print("Message arrived [");
 Serial.print(topic);
 Serial.print("] ");
 for (int i=0;i<length;i++) {
  char receivedChar = (char)payload[i];
  Serial.print(receivedChar);
  if (receivedChar == '0')
  // ESP8266 Huzzah outputs are "reversed"
  digitalWrite(BUILTIN_LED, HIGH);
  if (receivedChar == '1')
  digitalWrite(BUILTIN_LED, LOW);
  }
  Serial.println();
}


//Reconnect to MQTT function
void reconnect() {
 // Loop until we're reconnected
 int reconnect_tries = 0;
 while (!client.connected() && reconnect_tries < 20) {
 Serial.print("Attempting MQTT connection...");
 // Attempt to connect
 if (client.connect("ESP8266 Client")) {
  Serial.println("connected");
  // ... and subscribe to topic
  client.subscribe("ledStatus");
 } else {
  Serial.print("failed, rc=");
  Serial.print(client.state());
  Serial.println(" try again in 5 seconds");
  // Wait 5 seconds before retrying
  delay(5000);
  }
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
  WiFiClient client;
  const int httpPort = 1883; //80 by default

  if (!client.connected()) {
    reconnect();
    }
  //client.loop();

  int i = 100; //duty cycle %
  int j = 200; //steps to rotate, 200/rev
  int dlay = 2; //2ms between steps



  //            ***SET THE FEEDING PART HERE***               //
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
  M2.setmotor(_STOP);
  M1.setmotor( _STOP);
  //delay(1000);
  ////////////////////////////////////////////////////////////////

  //try to tell the pi we've fed the fishies
  while (//pi hasn't sent confirmation and fedsignal_tries < 20)
  {
    //send a 1 to the topic for the pi to read
    //look for confirmation from the pi
    //wait like, ten seconds
    }
  


  //try to connect again if no connection attempted before
  if (WiFi.status() != WL_CONNECTED){
    wifi_initialize();
  }
}

///////////////////////////////END/////////////////////////////////










  /*
  for (i=0; i=10; i++){
  M1.setmotor( _CCW, 200); //CCW facing the shaft
  M2.setmotor(_CW, 200);
  M1.setmotor( _CW, 200);
  M2.setmotor(_CCW, 200);
  }
  */

