// demo: CAN-BUS Shield, send data
#include <mcp_can.h>
#include <SPI.h>

// the cs pin of the version after v1.1 is default to D9
// v0.9b and v1.0 is default D10
const int SPI_CS_PIN = 10;
unsigned int received = 0;
MCP_CAN CAN(SPI_CS_PIN);                                    // Set CS pin

void setup()
{
    Serial.begin(115200);

    while (CAN_OK != CAN.begin(CAN_500KBPS))              // init can bus : baudrate = 500k
    {
        Serial.println("CAN BUS Shield init fail");
        Serial.println(" Init CAN BUS Shield again");
        delay(100);
    }
    Serial.println("CAN BUS Shield init ok!");
    
}

unsigned char mymessage[] = {11,12,13,14,15,16,17,18,19,420};
unsigned int canindex = 0x0;
void loop()

{
//    Serial.println("In loop");
    // send data:  id = 0x70, standard frame, data len = sizeof(data), stmp: data buf
    int i=0;
    int j=0;
    unsigned char packet[8];
    while (i<sizeof(mymessage)){
      packet[j]=mymessage[i];
      Serial.print(packet[i]);
      if (packet[7] != '\0'){
//        CAN.sendMsgBuf(0x70+canindex, 0, 8, packet);
        Serial.println("Sent message on " + 0x70+canindex);
        canindex+=0xF;
        j=0;
        memset(packet,'\0',8);
        
      }
      i++;
      j++;
    }
    delay(1000);
}

/*********************************************************************************************************
  END FILE
*********************************************************************************************************/

