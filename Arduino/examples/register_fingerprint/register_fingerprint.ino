/*
Register fingerprint image into ZF20 module internal database
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

    Serial.print(F("Connecting with module: "));
    if((resp = finger.VerifyPassword()) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Wait 10 sec for fingerprint */
    Serial.print(F("Waiting for finger on the sensor: "));
    uint32_t time = millis();
    uint32_t timeout = time + 10000;
    while((resp = finger.GenImage()) == NO_FINGER) {
        if(millis() > timeout) {
            Serial.println(F("No finger on sensor"));
            while(true);
        }
    }

    /* Check if everything is OK with the image */
    if(resp != INSTRUCTION_OK) {
        Serial.println(F("Error"));
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("Got finger"));
    }

    /* Generate image */
    Serial.print(F("Generating characteristics: "));
    if((resp = finger.Img2Tz(0x01)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Remove finger */
    Serial.println(F("Remove finger..."));
    while(finger.GenImage() != NO_FINGER);

    /* Wait 10 sec for fingerprint */
    Serial.print(F("Place same finger again: "));
    time = millis();
    timeout = time + 10000;
    while((resp = finger.GenImage()) == NO_FINGER) {
        if(millis() > timeout) {
            Serial.println(F("No finger on sensor"));
            while(true);
        }
    }

    /* Check if everything is OK with the image */
    if(resp != INSTRUCTION_OK) {
        Serial.println(F("Error"));
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("Got finger"));
    }

    /* Generate image */
    Serial.print(F("Generating characteristics: "));
    if((resp = finger.Img2Tz(0x02)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Merge */
    Serial.print(F("Merge: "));
    if((resp = finger.RegModel()) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Store model */
    Serial.print(F("Store model: "));
    if((resp = finger.StoreModel(0x01, 0x0010)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }
}

void loop()
{
}
