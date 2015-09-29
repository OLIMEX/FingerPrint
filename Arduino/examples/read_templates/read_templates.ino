/*
Print usage for template databese of ZF20 module
Copyright (C) 2015  Stefan Mavrodiev, OLIMEX LTD.
Contact: support@olimex.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
*/

#include <SoftwareSerial.h>
#include <FingerPrint.h>

/*
Define default ADDRESS and PASSWORD for communicating with the module
*/
#define ADDRESS 0xFFFFFFFF
#define PASSWORD 0x00000000

/*
Start new software serial.
If you're using OLIMEXINO-32U4 only the following pins can be used for RX:
8, 9, 10, 11, 14, 15, 16.
You also can use hardware serial "Serial1"
*/
SoftwareSerial mySerial(8, 9);

/*
Create new object
*/
FingerPrint finger(mySerial, ADDRESS, PASSWORD);

void setup()
{
    response_t resp;
    uint8_t table_data[32];
    /*
    Before start using the module serial must be set.
    */
    Serial.begin(9600);
    mySerial.begin(57600);

    /*
    Make loading like delay
    */
    for(int i = 0; i < 10; i++)
    {
        Serial.print(".");
        delay(500);
    }
    Serial.println("");

    // finger.SetVerbose(true);

    /* Connect with module */
    Serial.print(F("Connecting with module: "));
    if((resp = finger.VerifyPassword()) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Read table data */
    for(uint8_t t = 0; t < 4; t++){
        if((resp = finger.ReadTemplateTable(t, table_data)) != INSTRUCTION_OK) {
            finger.PrintResponse(resp);
            while(true);
        } else {
            Serial.print(F("Table "));
            Serial.println(t);
            Serial.println(F("  0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F"));
            for(int i = 0; i < 32; i++) {
                for(uint8_t j = 0x01; j != 0; j <<= 1)
                    if(table_data[i] & j) {
                        Serial.print(F("  x"));
                    } else {
                        Serial.print(F("  ."));
                    }
                    if(i % 4 == 3) {
                        Serial.println(F(""));
                    }

                // Serial.println(table_data[i]);
            }
        }
    }

    /* Read total number of templates */
    uint16_t count;
    if((resp = finger.ReadTemplateNumber(&count)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.print(F("Total: "));
        Serial.println(count);
    }
}

void loop()
{
}
