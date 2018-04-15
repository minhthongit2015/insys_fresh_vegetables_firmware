
#include <RS485.h>
#include <SoftwareSerial.h>
#include "DHT.h"

#define DEBUG
#define debug(title, msg) { Serial.print(title); Serial.println(msg); }

// RS485 adjust
#define MAX_BUF_LEN (maxMsgLen+3+1)

// DHT settings
#define DHTPIN 2
#define DHTTYPE DHT21
DHT dht(DHTPIN, DHTTYPE);


char recvBuf[MAX_BUF_LEN] = {"\0"};
float volt,t;

char stationID[] = {"B1"};

unsigned int Serial_Baudrate = 9600;
unsigned int RS485_Baudrate = 19200;

// Functions
char* pack(char msg[], char* outmsg);
char* packSensorData(float temp, float humi, byte temp_precision=2, byte humi_precision=0);

bool sendMessage(char msg[]);
bool sendSensorData(float temp, float humi, byte temp_precision=2, byte humi_precision=0);

void setup()
{
  Serial.begin(Serial_Baudrate);
  Serial.print("System Startup: Station [");
  Serial.print(stationID);
  Serial.println("]");

  RS485_Begin(RS485_Baudrate);
  dht.begin();
  delay(100);

  sendMessage(stationID);
  debug("Handshake: ", stationID);
}

void loop()
{
  while (true) {
    if(recvMessage()) {
      debug("Recv: ", unpack(recvBuf));

      sendMessage("OK");
    } else {
      if (recvBuf[0] != 0) {
        debug("Recv e: ", recvBuf);
      }
    }
  }
}

char* pack(char msg[])
{
  static char sendbuf[MAX_BUF_LEN] = {"\0"};
  sprintf(sendbuf, "#%s\n", msg);
  debug("sendbuf: ", sendbuf)
  return sendbuf;
}

char* packSensorData(float temp, float humi, byte temp_precision, byte humi_precision)
{
  static char buf[MAX_BUF_LEN] = {"\0"};
  sprintf(buf, "T\%.%df_H\%.%df", temp_precision, humi_precision);
  debug("format: ", buf)
  sprintf(buf, buf, temp, humi);
  debug("sensors: ", buf)
  return pack(buf);
}

char* unpack(char msg[])
{
  static char buf[MAX_BUF_LEN] = {"\0"};
  static char *p1;
  p1 = strtok(msg, "#");
  p1 = strtok(NULL, "\n");
  // strncpy(recvBuf, msg+1);
  return p1;
}

bool sendMessage(char msg[])
{
  return RS485_SendMessage(pack(msg), fWrite, ENABLE_PIN);
}

bool sendSensorData(float temp, float humi, byte temp_precision, byte humi_precision)
{
  return RS485_SendMessage(packSensorData(temp, humi, temp_precision, humi_precision), fWrite, ENABLE_PIN);
}

bool recvMessage()
{
  return RS485_ReadMessage(fAvailable, fRead, recvBuf);
}



