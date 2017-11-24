#include <Wire.h>
#define __DEBUG__
//#undef __DEBUG__

#define SensorPin A0        // pH data pin
#define ArrayLenth 40       // sample array lenght
#define SLAVE_ADDRESS 0x04  // i2c address

int pHArray[ArrayLenth];    // store the average value of the sensor feedback
int pHArrayIndex = 0;       // current index in array
union {
  float floatVal;
  byte bytes[4];
} pHValue;
float Offset = -0.42;         //deviation compensate
long samplingInterval = 100;
long printInterval = samplingInterval*ArrayLenth;

void setup(void)
{
  #ifdef __DEBUG__
    Serial.begin(9600);
    Serial.println("<*> pH meter SEN0161 <*>");
    Serial.println("[SYS] > pH meter SEN0161");
    Serial.println("[SYS] > sensor pin by default: A3");
    Serial.println("[SYS] > i2c address by default: 0x04");
    Serial.println("[SYS] > sampling interval by default: 0x04");
  #endif

  // I2C setup
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
}

void loop(void)
{
  pHArray[pHArrayIndex++] = analogRead(SensorPin);
  if (pHArrayIndex == ArrayLenth) pHArrayIndex = 0;
  delay(samplingInterval);
  #ifdef __DEBUG__
    static unsigned long printTime = millis();
    static float voltage;
    if (millis() - printTime > printInterval)
    {
      voltage = avergearray(pHArray, ArrayLenth) * 5.0 / 1024;
      Serial.print("Voltage:");
      Serial.print(voltage, 2);
      Serial.print("    pH value: ");
      Serial.println(3.5 * voltage + Offset, 2);
      printTime = millis();
    }
  #endif
}

double avergearray(int * arr, int length){
  int i;
  int max, min;
  long amount= 0;
  if (length <= 0) {
    Serial.println("Error number for the array to avraging!/n");
    return 0;
  }
  if (length < 5) {   //less than 5, calculated directly statistics
    for (i = 0; i < length; i++) amount += arr[i];
    return ((double)amount) / length;
  } else {
    if (arr[0] < arr[1]) { min = arr[0]; max = arr[1]; }
    else { min = arr[1]; max = arr[0]; }
    for (i = 2; i < length; i++) {
      if (arr[i] < min) {
        amount += min;
        min = arr[i];
      } else {
        if (arr[i] > max) {
          amount += max;    //arr>max
          max = arr[i];
        } else {
          amount += arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    return ((double)amount)/(length - 2);
  }//if
}

void receiveData(int byteCount){
  int number = 0;
  while (Wire.available()) {
    number = Wire.read();
//    Serial.print("data received: ");
//    Serial.println(number);
  }
}
void sendData() {
  double voltage = avergearray(pHArray, ArrayLenth) * 5.0 / 1024;
  pHValue.floatVal = 3.5 * voltage + Offset;
  #define testz
  #ifdef test
  Serial.print(pHValue.bytes[0]); Serial.print(",");
  Serial.print(pHValue.bytes[1]); Serial.print(",");
  Serial.print(pHValue.bytes[2]); Serial.print(",");
  Serial.print(pHValue.bytes[3]);
  #endif
  Wire.write(pHValue.bytes, 4);
}
