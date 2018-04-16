
#include <RS485.h>
#include <SoftwareSerial.h>
#include "DHT.h"
// #include <Adafruit_Sensor.h>
// #include <DHT.h>
// #include <DHT_U.h>

#define DEBUG
#define debug(title, msg) { Serial.print(title); Serial.println(msg); }


/*********************************************
 *            Điều Chỉnh Thông Số            *
 *********************************************/

// ID phân biệt trạm
char stationID[] = {"B1"};
#define SendStationIdentify { sendMessage("", 'I'); debug("Hello I'm ", stationID) }

// Tín hiệu bắt đầu một thông điệp
char signature = '#';
// Tín hiệu kết thúc một thông điệp
char terminator = '\n';

enum Device {
  MotorPin = 5,        // Pin điều khiển Motor bơm
  MotorRotatePin = 6,  // Pin điều khiển Motor xoay trụ
  LightPin = 7,        // Pin điều khiển hệ thống ánh sáng nhân tạo
  ConnectedPin = 8     // Pin điều khiển đèn báo đã kết nối trung tâm chưa
};

// Baudrate
int SerialBaudrate = 9600;
int RS485Baudrate = 19200;

// Thiết đặt cho cảm biến nhiệt độ độ ẩm DHT
#define DHTPIN 2
#define DHTTYPE DHT21

/******************** END ********************/



/*** Bộ đệm, biến dùng cho tính toán, xử lý ***/
// Bộ đệm toàn cục để lưu thông điệp đọc được từ rs485
char rs485Buf[maxMsgLen + 3 + 1] = {"\0"};
// Biến toàn cục lưu con trỏ trỏ tới nội dung thông điệp chính (trỏ tới vùng thông điệp trong rs485Buf)
char *msg = NULL;

// Đối tượng cảm biến DHT
DHT dht(DHTPIN, DHTTYPE);

// Trạng thái thiết lập liên kết với trung tâm
bool isConnectEstablish = false;


/*** Một số hàm hỗ trợ truyền nhận dữ liệu ***/

// Đóng gói thông điệp
char* pack(char msg[]);

// Gửi thông điệp
bool sendMessage(char msg[]);
bool sendSensorData(byte temp_precision=1, byte humi_precision=0);

// Nhận thông điệp
bool recvMessage();
bool unpack();

bool switchDevice(char deviceType, char state);

/*********************************************
 *            Bắt Đầu Chương Trình           *
 *********************************************/

void setup()
{
  Serial.begin(SerialBaudrate);
  Serial.print("System Startup: Station [");
  Serial.print(stationID);
  Serial.println("]");

  RS485_Begin(RS485Baudrate);
  dht.begin();

  pinMode(MotorPin, OUTPUT);
  pinMode(MotorRotatePin, OUTPUT);
  pinMode(LightPin, OUTPUT);
  pinMode(ConnectedPin, OUTPUT);

  // Báo lên trung tâm rằng trạm vừa khởi động
  SendStationIdentify
  debug("Handshake: ", stationID);
}

void loop()
{
  char msgType;
  char *msgStationID;
  char *part = NULL, *pMsg = NULL;

  #define first pMsg = &msg[2]; msgStationID = strtok(pMsg, "_");
  #define next part = strtok(NULL, "_");
  #define isMine (!strcmp(msgStationID, stationID))

  while (true) {
    if(recvMessage()) {
      debug("Recv: ", msg);
      
      if (!strcmp(msg, "GETALL")) {  // Nhận được yêu cầu gửi lại thông tin định danh tất cả trạm từ trung tâm
        SendStationIdentify debug("Server Get Info All!","")
      } else {
        // Lấy loại thông điệp
        msgType = msg[0];

        // Lấy ID trạm
        first

        // Kiểm tra phải thông điệp gửi đến trạm này không
        if (!isMine) continue;

        switch (msgType) {
          case 'I': // Nhận được yêu cầu gửi lại thông tin định danh trạm từ trung tâm
            isConnectEstablish = false; debug("Server Get Info!","")
            SendStationIdentify break;
          case 'A': debug("Connect Established!","")
            isConnectEstablish = true;
            switchDevice('C', '1');
            break;
          case 'S': // Nhận được yêu cầu gửi lại dữ liệu cảm biến
            sendSensorData();
            break;
          case 'C':
            next  // Lấy thông tin thiết bị cần bật và trạng thái
            if (part) debug("dev:", part)
            switchDevice(part[0], part[1]);
            break;
          default:
            break;
        }
      }
    }
    delay(50);
  }
}


/*********************************************
 *       Định Nghĩa Các Hàm Chức Năng        *
 *********************************************/

// Đóng gói thông điệp
char* pack(char msg[], char msgType)
{
  static char sendbuf[maxMsgLen] = {"\0"};
  if (msg[0]) sprintf(sendbuf, "#%c_%s_%s\n", msgType, stationID,  msg);
  else sprintf(sendbuf, "#%c_%s\n", msgType, stationID);
  debug("sendbuf: ", sendbuf)
  return sendbuf;
}

// Gửi thông điệp
bool sendMessage(char msg[], char msgType)
{
  return RS485_SendMessage(pack(msg, msgType), fWrite, ENABLE_PIN);
}

bool sendSensorData(byte temp_precision, byte humi_precision)
{
  static float temp = 0, humi = 0;
  static char tempBuf[10] = {"\0"}, humiBuf[10] = {"\0"};
  static char sensorbuf[maxMsgLen] = {"\0"};

  temp = dht.readTemperature();
  humi = dht.readHumidity();
  dtostrf(temp, temp_precision+3, temp_precision, tempBuf);
  dtostrf(humi, humi_precision+3, temp_precision, humiBuf);
  sprintf(sensorbuf, "T%s_H%s", tempBuf, humiBuf);
  debug("sensors: ", sensorbuf)
  return RS485_SendMessage(pack(sensorbuf, 'S'), fWrite, ENABLE_PIN);
}

// Nhận thông điệp
bool recvMessage()
{
  bool change = RS485_ReadMessage(fAvailable, fRead, rs485Buf);
  if (!change) return false;

  if (change) {
    if (unpack()) { // Kiểm tra thông điệp có đúng cấu trúc không
      return true;
    } else {
      return false;
    }
  }
}

// Giả xử bộ đệm luôn nhận đúng và đủ thông điệp; có bắt đầu, có kết thúc (Thông điệp luôn ngắn vừa đủ, nhỏ hơn 20 ký tự)
// - Trỏ msg về điểm bắt đầu thông điệp (Bỏ qua tín hiệu bắt đầu)
// - Xóa ký tự ngắt thông điệp
bool unpack()
{
  // static char buf[MAX_BUF_LEN] = {"\0"};
  // Kiểm tra recvBuf[] có dữ liệu hay không
  if (!rs485Buf[0]) return false;

  // Bỏ qua ký hiệu '#' bắt đầu thông điệp
  msg = &rs485Buf[1];

  // Xóa ký tự ngắt thông điệp trong rs485Buf[]
  byte i = 1;
  while (rs485Buf[i] != '\0' && rs485Buf[i] != terminator) ++i;
  rs485Buf[i] = '\0';

  return true;
}


bool switchDevice(char deviceType, char state)
{
  byte pin = 0;
  if (deviceType == 'M') pin = MotorPin;
  else if (deviceType == 'R') pin = MotorRotatePin;
  else if (deviceType == 'L') pin = LightPin;
  else if (deviceType == 'C') pin = ConnectedPin;
  Serial.print("dev:"); Serial.print(deviceType); Serial.print(state);
  digitalWrite(pin, state == '0' ? 0 : 1);
  return state == '0' ? 0 : 1;
}










