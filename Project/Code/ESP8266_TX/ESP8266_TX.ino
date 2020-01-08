// Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/11/28.
// Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

#include <SPI.h>
#include <RH_RF95.h>
#include <DHT.h>
#include <string.h>

/* IMPORTANT: "ID:X" The ID of sensor node, which is print on box. Once deployed, Location and ID should be reported to MongoDB */
#define node_ID "ID:11"

/* DHT22 temperature and humidity sensor define */
#define DHTPIN 5     // Digital pin connected to the DHT sensor
// Feather HUZZAH ESP8266 note: use pins 4, 5 (which usually used as I2C, but we don't have I2C device)
// Pin 15 can work but DHT must be disconnected during program upload.
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321. https://learn.adafruit.com/dht/overview

/* Capacitive soil moisture sensor define */
#define SoilMoistureSensor A0 // "ADC Pin"

/* RFM95 LoRa define */
#define RFM95_CS  2    // "E"
#define RFM95_RST 0   // "C"
#define RFM95_INT 15   // "B"
#define RF95_FREQ 915.0
// Change to 434.0 or other frequency, must match RX's freq!
// The frequency range designated to LoRa Technology in the United States, Canada and South America is 902 to 928 MHz. 
// This frequency range is known as the 915 MHz frequency banjjjd.
#define MessageLength 100

/* creat DHT22 temperature and humidity sensor instance */
DHT dht(DHTPIN, DHTTYPE);

/* creat RFM95 LoRa instance */
RH_RF95 rf95(RFM95_CS, RFM95_INT);

/* predefine soil moisture sensor calibration value */
const float AirValue = 904; //you need to change this value that you had recorded in the air 
const float WaterValue = 528; //you need to change this value that you had recorded in the water 
float intervals = AirValue - WaterValue;

void setup()
{
  // initialize DHT22 temperature and humidity sensor
  Serial.begin(115200);
  Serial.println(F("DHTxx test!"));
  dht.begin();
  // DHT22 initialize end

  delay(10);

  // initialize RFM95 LoRa wireless communication
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);


  // Remove the while (!Serial); line if you are not tethering to a computer, as it will cause the Feather to halt until a USB connection is made!
//  while (!Serial) {
//    delay(1);
//  }

  delay(100);

  Serial.println("Feather LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1); // security code. When the user does something very bad with an embedded device, it can be good to block them from trying anything else. Need manually reboot.
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

}

//int16_t packetnum = 0;  // packet counter, we increment per xmission.
// Deep sleep mode can't count packet number. Memory will be erased once sleep. 

void loop()
{
  // Measure
  delay(3000);
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float humidity = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float tempurature_C = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  // float tempurature_F = dht.readTemperature(true);
  Serial.println(analogRead(SoilMoistureSensor));
  float soil_moisture = (AirValue - analogRead(SoilMoistureSensor))/intervals; // Relative soil moisture to air moisture
  Serial.println(soil_moisture);
  
  // Check if any reads failed, use 9999 to replace that.
  if (isnan(humidity)) {
    humidity = 9999;
  }
  if (isnan(tempurature_C)) {
    tempurature_C = 9999;
  }

  // Message to send
  Serial.println("Transmitting..."); // Send a message to rf95_server
  char radiopacket[MessageLength];
  char humidity_Str[]="?RH:               ";
  char tempurature_C_Str[]="?TP:               ";
  char moisture_Str[]="?SM:               ";
  // char series_Str[]="No.      ";
  gcvt(humidity,4,humidity_Str+4);      // convert float to string
  gcvt(tempurature_C,4,tempurature_C_Str+4);
  gcvt(soil_moisture,4,moisture_Str+4);
  // itoa(packetnum++, series_Str+3, 10);  // convert int to string
//  Serial.println(humidity);
//  Serial.println(tempurature_C);
//  Serial.println(soil_moisture);
//  Serial.println(humidity_Str);
//  Serial.println(tempurature_C_Str);
//  Serial.println(moisture_Str);
  strcpy(radiopacket,node_ID);
  strcat(radiopacket,humidity_Str);     // combine string
  strcat(radiopacket,tempurature_C_Str);
  strcat(radiopacket,moisture_Str);
  // strcat(radiopacket,series_Str);

  // Send begin
  Serial.print("Sending "); Serial.println(radiopacket);
  radiopacket[MessageLength-1] = 0;
  Serial.println(sizeof(radiopacket));
  
  Serial.println("Sending...");
  delay(10);
  rf95.send((uint8_t *)radiopacket, sizeof(radiopacket));

  Serial.println("Waiting for packet to complete..."); 
  delay(10);
  rf95.waitPacketSent(5000);
  
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  Serial.println("Waiting for reply...");
  if (rf95.waitAvailableTimeout(1000))
  { 
    // Should be a reply message for us now   
    if (rf95.recv(buf, &len))
   {
      Serial.print("Got reply: ");
      Serial.println((char*)buf);
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);    
    }
    else
    {
      Serial.println("Receive failed");
    }
  }
  else
  {
    Serial.println("No reply, is there a listener around?");
  }
  rf95.sleep(); // set RFM95 LoRa to sleep mode to save energy. It will be activated when send() is called

  // One life cycle end
  ESP.deepSleep(10e6); // Set ESP8266 to deep sleep mode, only enable RTC. Irq deep sleep mode needs to connect Pin16 and RST.
  // Attention: The RST on RFM95 surface is for reset of RFM95. The RST on RFM95 edge is for reset of ESP8266.
  // Do NOT use Pin 16 (which is used for ESP8266 deep sleep mode) as the reset of RFM95 when Pin 16 is wired to RST on ESP8266 (edge RST on RFM95) 

}
