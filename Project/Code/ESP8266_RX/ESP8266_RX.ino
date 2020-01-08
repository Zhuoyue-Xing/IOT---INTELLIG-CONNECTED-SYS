// Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/11/28.
// Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

#include <SPI.h>
#include <RH_RF95.h>
#include <NTPClient.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <WiFiUdp.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

/* RFM95 LoRa define */
#define RFM95_CS  2    // "E"
#define RFM95_RST 16   // "D"
#define RFM95_INT 15   // "B"
#define RF95_FREQ 915.0
// Change to 434.0 or other frequency, must match RX's freq!
// The frequency range designated to LoRa Technology in the United States, Canada and South America is 902 to 928 MHz. 
// This frequency range is known as the 915 MHz frequency band.
/* RFM95 LoRa define end */

// Blinky on receipt
#define LED 13

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

// // WiFi credentials.
// const char* WIFI_SSID = "Columbia University";
// const char* WIFI_PASS = "";

const long utcOffsetInSeconds = -18000; //For UTC -5.00 : -5 * 60 * 60 : -18000

char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};


// WiFiClientSecure wifiClient;   // Singleton instance of wifi

ESP8266WiFiMulti wifiMulti;      // Create an instance of the ESP8266WiFiMulti class, called 'wifiMulti'

WiFiUDP UDP;                     // Create an instance of the WiFiUDP class to send and receive

// Define NTP Client to get time
NTPClient timeClient(UDP, "pool.ntp.org", utcOffsetInSeconds);


void startWiFi() { // Try to connect to some given access points. Then wait for a connection
  wifiMulti.addAP("Columbia University", "");   // add Wi-Fi networks you want to connect to
  wifiMulti.addAP("Rock_NYC", "Columbia_SEAS_1754");
  // wifiMulti.addAP("ssid_from_AP_3", "your_password_for_AP_3");

  Serial.println("Connecting");
  while (wifiMulti.run() != WL_CONNECTED) {  // Wait for the Wi-Fi to connect
    delay(250);
    Serial.print('.');
  }
  Serial.println("\r\n");
  Serial.print("Connected to ");
  Serial.println(WiFi.SSID());             // Tell us what network we're connected to
  Serial.print("IP address:\t");
  Serial.print(WiFi.localIP());            // Send the IP address of the ESP8266 to the computer
  Serial.println("\r\n");
}


void ReportData(uint32_t currentTime, char* ID, char* humidity, char* temperature, char* soil_moisture)
{
  HTTPClient http;
  http.begin("http://3.87.68.197:8099/sensordata/post");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Accept", "application/json");

  /* Create JSON payload to sent to MongoDB
    {
      "Datetime": 1000,
      "ID": "01",
      "humidity": "22",
      "soil_moisture": "42",
      "temperature": "-3"
    }
  */

  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  
  root["Datetime"] = currentTime;
  root["ID"] = ID;
  root["humidity"] = humidity;
  root["temperature"] = temperature;
  root["soil_moisture"] = soil_moisture;
  String buffer;
  root.printTo(buffer);

  int httpCode = http.POST(buffer);

  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      Serial.println("Data stored in MongoDB");
    } else {
      Serial.println("Failed to store data");
      if (httpCode == 400) {
        Serial.println("Validation error: The device ID, access key, or access secret is not in the proper format.");
      } else if (httpCode == 401) {
        Serial.println("Invalid credentials");
      } else {
        Serial.println("Unknown response from API");
      }
      return;
    }
  } else {
    Serial.println("Failed to connect to MongoDB.");
    return;
  }

  http.end();
}


void setup()
{
  pinMode(LED, OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(115200);

  // initialize RFM95 LoRa wireless communication
  delay(100);
  Serial.println("Feather LoRa RX Test!");
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  // RFM95 LoRa initialize end

  startWiFi();                   // Try to connect to some given access points. Then wait for a connection

  timeClient.begin();

  timeClient.update();
}



void loop()
{

  // RFM95 LoRa receive
  if (rf95.available())
  {
    // Should be a message for us now
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (rf95.recv(buf, &len))  // lora received a message
    {
      digitalWrite(LED, HIGH);
      RH_RF95::printBuffer("Received: ", buf, len);
      Serial.print("Got: ");
      Serial.println((char*)buf);
       Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);

      // Send a reply
      uint8_t data[] = "RCVD";
      rf95.send(data, sizeof(data));
      rf95.waitPacketSent();
      Serial.println("Sent a reply");
      digitalWrite(LED, LOW);

      // Once recieve a data from sensor node, report the data to MongoDB

      // Update the current time
      timeClient.update();
      
      // Split the message lora received
      char delim[] = " :?";  

      char *s = strdup((char*)buf);  
      char *token; 
      char *key1;
      char *value1;
      char *key2;
      char *value2;
      char *key3;
      char *value3;
      char *key4;
      char *value4;
      token = strsep(&s, delim);
      key1=token;
      token = strsep(&s, delim);
      value1=token;
      token = strsep(&s, delim);
      key2=token;
      token = strsep(&s, delim);
      value2=token;
      token = strsep(&s, delim);
      key3=token;
      token = strsep(&s, delim);
      value3=token;
      token = strsep(&s, delim);
      key4=token;
      token = strsep(&s, delim);
      value4=token;
      
      
      uint32_t currentTime = timeClient.getEpochTime();
      
      ReportData(currentTime, value1, value2, value3, value4);

      Serial.print("Time: ");
      Serial.print(daysOfTheWeek[timeClient.getDay()]);
      Serial.print(", ");
      Serial.print(timeClient.getHours());
      Serial.print(":");
      Serial.print(timeClient.getMinutes());
      Serial.print(":");
      Serial.println(timeClient.getSeconds());
      
    }
    else      // some error when receiving the message
    {
      Serial.println("Receive failed");
    }
  }
}
