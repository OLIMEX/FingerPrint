#ifndef __FINGER_PRINT_H
#define __FINGER_PRINT_H

#include "Arduino.h"

typedef enum {
    OK = 0x01,
    DATA = 0x02,
    ACK = 0x07,
    END_DATA = 0x08
}packet_identification_t;

typedef enum {
    INSTRUCTION_OK = 0x00, // represents the instruction is finished or OK;
    RECEIVE_ERROR = 0x01, // represents packet receive error;
    NO_FINGER = 0x02, // that there is no finger on the sensor;
    INPUT_IMAGE_FAILED = 0x03, // represents input fingerprint image failed;
    INPUT_IMAGE_MESSY = 0x06, // represents the fingerprint image is not too messy and health characteristics;
    INPUT_IMAGE_SMALL = 0x07, // represents the fingerprint image is normal, but too few feature points (or too small) feature is not born;
    FINGERPRINT_MISMATCH = 0x08, // represents fingerprint mismatch;
    FINGERPRINT_NOT_SEARCH = 0x09, // represents not search the fingerprint;
    MERGE_FAILED = 0x0A, // failure was characterized by the merger;
    ADDRESS_TOO_BIG = 0x0b, // indicates the address number when accessing fingerprint database beyond the scope of the fingerprint database;
    DATABASE_READ_ERROR = 0x0C, // indicates a read error or invalid template from the fingerprint database;
    FEATURE_UPLOAD_FAILED = 0x0d, // Upload feature indicates failure;
    CANT_ACCEPT_DATA = 0x0E, // indicates that the module can not accept the subsequent data packet;
    IMAGE_UPLOAD_FAILED = 0x0F, // Upload your image indicates failure;
    TEMPLATE_DELETE_FAILED = 0x10, // delete the template indicates failure;
    EMPTY_DATABASE_FAILED = 0x11, // Empty fingerprint database indicates failure;
    INCORRECT_PASSWORD = 0x13, // means that the password is incorrect;
    INCORRECT_BUFFER = 0x15, // that there is no buffer zone is not a valid original picture image is born;
    FLASH_ERROR = 0x18, // represents read and write FLASH error;
    INVALID_REGISTER = 0x1a, // Invalid register number;
    INVALID_ADDRESS = 0x20, // address code error;
    PASSWORD_NOT_VERIFIED = 0x21, // password must be verified;
}response_t;

class FingerPrint
{
    public:
        FingerPrint(Stream&, uint32_t password, uint32_t address);

        void SetVerbose(bool verbose);
        void PrintResponse(uint8_t response);

        void set_password(uint32_t password);
        void set_address(uint32_t address);

        response_t VerifyPassword();
        response_t SetPassword(uint32_t new_password);
        response_t SetAddress(uint32_t new_address);
        response_t ReadTemplateTable(uint8_t page, uint8_t *table);
        response_t ReadTemplateNumber(uint16_t *count);

        // Fingerprint related methods
        response_t GenImage();
        response_t Img2Tz(uint8_t buffer_id);
        response_t RegModel();
        response_t StoreModel(uint8_t buffer_id, uint16_t position);
        response_t Empty();
        response_t LoadChar(uint8_t buffer_id, uint16_t position);
        response_t DeleteChar(uint16_t start, uint16_t count);
        response_t Match(uint16_t *score);
        response_t Search(uint8_t buffer_id, uint16_t start, uint16_t count, uint16_t *position, uint16_t *score);



    private:
        uint32_t __address;
        uint32_t __password;

        Stream& __serial;

        bool __verbose;

        void debug(char *format, ...);

        // Communication methods
        uint16_t CalculateChecksum(uint8_t *packet, uint16_t packet_len, uint8_t packet_type);
        uint8_t SendPacket(uint8_t *packet, uint16_t packet_len, packet_identification_t packet_id);
        uint8_t ReadPacket(uint8_t *packet, uint16_t packet_len, packet_identification_t packet_id);

};
#endif
