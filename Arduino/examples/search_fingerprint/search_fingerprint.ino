/*
Search the databese for matching fingerprint
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
// SoftwareSerial mySerial(8, 9);

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
    /*
    Try to verify module password
    */
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

    /* Search for fingerprint in the database */
    uint16_t position;
    uint16_t score;
    Serial.print(F("Searching: "));
    if((resp = finger.Search(0x01, 0, 1024, &position, &score)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
        Serial.print(F("Position: "));
        Serial.println(position);
        Serial.print(F("Score: "));
        Serial.println(score);
    }

    /* Load char in buffer 2 */
    /* This will load found fingerprint at position to
    CharBuffer2. This is used only for the demonstration,
    otherwise is useless like this.
    */
    Serial.print(F("Loading char: "));
    if((resp = finger.LoadChar(0x02, position)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Wait 10 sec for fingerprint */
    Serial.print(F("Place the same finger on the sensor: "));
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
    if((resp = finger.Img2Tz(0x01)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }

    /* Remove finger */
    Serial.println(F("Remove finger..."));
    while(finger.GenImage() != NO_FINGER);

    /* Match buffer1 and buffer2 */
    Serial.print(F("Matching fingerprint: "));
    /*
    Match will compare CharBuffer1 with CharBuffer2
    and will return compare score.
    */
    if((resp = finger.Match(&score)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
        Serial.print(F("Score: "));
        Serial.println(score);
    }

    /* Delete fingerprint */
    Serial.print(F("Deleting found fingerprint: "));
    /*
    DeleteChar will delete N count fingerprints from given position.
    In this case only the fingerprint at position will be erased.
    */
    if((resp = finger.DeleteChar(position, 1)) != INSTRUCTION_OK) {
        finger.PrintResponse(resp);
        while(true);
    } else {
        Serial.println(F("OK"));
    }
}

void loop()
{
}
