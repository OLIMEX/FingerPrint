#include "FingerPrint.h"

#define U32_TO_ARRAY(arg) \
    arg >> 24 & 0xFF, arg >> 16 & 0xFF, arg >> 8 & 0xFF, arg & 0xFF

#define U16_TO_ARRAY(arg) \
    arg >> 8 & 0xFF, arg & 0xFF

char print_buffer[100];
uint8_t rx_buffer[50];
uint8_t tx_buffer[20];




// Default constructor
FingerPrint::FingerPrint(Stream& serial, uint32_t address, uint32_t password) :
    __serial(serial), __address(address), __password(password)
{
    __verbose = false;
}

void FingerPrint::set_password(uint32_t password) {
    __password = password;
}

void FingerPrint::set_address(uint32_t address) {
    __address = address;
}

void FingerPrint::SetVerbose(bool verbose)
{
    __verbose = verbose;
}
void FingerPrint::debug(char *format, ...) {
    if(__verbose) {

        va_list args;

        va_start(args, format);
        vsprintf(print_buffer, format, args);
        va_end(args);
        Serial.print(print_buffer);
    }
}

uint16_t FingerPrint::CalculateChecksum(uint8_t *packet, uint16_t packet_len, uint8_t packet_type)
{

    uint16_t sum = 0;
    uint8_t len = packet_len + 2;

    sum = ((len >> 8) & 0xFF) + (len & 0xFF) + packet_type;

    for(int i = 0; i < packet_len; i++) {
        sum += packet[i];
    }
    return sum;
}

uint8_t FingerPrint::SendPacket(uint8_t *packet, uint16_t packet_len, packet_identification_t packet_id)
{
    // Add magic header
    tx_buffer[0] = 0xef;
    tx_buffer[1] = 0x01;

    // Add device address
    tx_buffer[2] = __address >> 24 & 0xFF;
    tx_buffer[3] = __address >> 16 & 0xFF;
    tx_buffer[4] = __address >> 8 & 0xFF;
    tx_buffer[5] = __address >> 0 & 0xFF;

    // Add packet type
    tx_buffer[6] = packet_id;

    // Add packet len
    tx_buffer[7] = (packet_len + 2) >> 8 & 0xFF;
    tx_buffer[8] = (packet_len + 2) >> 0 & 0xFF;

    // Add data
    for(int i = 0; i < packet_len; i++) {
        tx_buffer[9+i] = packet[i];
    }

    // Add checksum
    uint16_t checksum = CalculateChecksum(packet, packet_len, packet_id);
    tx_buffer[9 + packet_len] = checksum >> 8 & 0xFF;
    tx_buffer[10 + packet_len] = checksum & 0xFF;

    debug("Sending: ");
    for(int i = 0; i < 11 + packet_len; i++) {
        debug("%02x ", tx_buffer[i]);
        __serial.write(tx_buffer[i]);
    }
    debug("\n");

}

uint8_t FingerPrint::ReadPacket(uint8_t *packet, uint16_t packet_len, packet_identification_t packet_id)
{
    uint8_t i = 0;
    uint16_t sum = 0;

    debug("Reading: ");

    uint32_t time = millis();
    time += 1000;
    while(true) {
        while(__serial.available() > 0) {
            rx_buffer[i] = __serial.read();
            debug("%02x ", rx_buffer[i]);
            i++;
        }
        if(i == packet_len+11) {
            break;
        }
        if(millis() > time){
            break;
        }
    }
    debug("\n");

    if(!i) {
        Serial.println(F("Error: Nothing was read"));
        return 1;
    }

    // Check magic header
    if (rx_buffer[0] != 0xef || rx_buffer[1] != 0x01) {
        Serial.println(F("Error: Magic header does not match!"));
        return 1;
    }

    if ((rx_buffer[2] != (__address >> 24 & 0xFF)) ||
        (rx_buffer[3] != (__address >> 16 & 0xFF)) ||
        (rx_buffer[4] != (__address >> 8 & 0xFF)) ||
        (rx_buffer[5] != (__address >> 0 & 0xFF))) {
        Serial.println(F("Error: Device address does not match!"));
        return 1;
    }

    if (rx_buffer[6] != packet_id) {
        Serial.println(F("Error: Packet identification does not match!"));
        return 1;
    }

    if (rx_buffer[7] != ((packet_len + 2) >> 8 & 0xFF) || rx_buffer[8] != ((packet_len +2)  & 0xFF)) {
        Serial.println(F("Error: Packet length does not match!"));
        return 1;
    }

    sum = CalculateChecksum(&rx_buffer[9], packet_len, packet_id);
    if(rx_buffer[9 + packet_len] != (sum >> 8 & 0xFF) || rx_buffer[10 + packet_len] != (sum & 0xFF)) {
        Serial.println(F("Error: Packet checksum does not match!"));
        return 1;
    }

    for(int i = 0; i < packet_len; i++) {
        packet[i] = rx_buffer[9+i];
    }

    return 0;
}

void FingerPrint::PrintResponse(uint8_t response)
{
    switch(response) {
        case INSTRUCTION_OK:
            Serial.println(F("OK"));
            break;

        case RECEIVE_ERROR:
            Serial.println(F("Receive error"));
            break;

        case NO_FINGER:
            Serial.println(F("No finger"));
            break;

        case INPUT_IMAGE_FAILED:
            Serial.println(F("Input fingerprint image failed"));
            break;

        case INPUT_IMAGE_MESSY:
            Serial.println(F("Image is not too messy"));
            break;

        case INPUT_IMAGE_SMALL:
            Serial.println(F("Too few feature points"));
            break;

        case FINGERPRINT_MISMATCH:
            Serial.println(F("Fingerprint mismatch"));
            break;

        case FINGERPRINT_NOT_SEARCH:
            Serial.println(F("Search failed"));
            break;

        case MERGE_FAILED:
            Serial.println(F("Merge failed"));
            break;

        case ADDRESS_TOO_BIG:
            Serial.println(F("Database address too big"));
            break;

        case DATABASE_READ_ERROR:
            Serial.println(F("Database read error"));
            break;

        case FEATURE_UPLOAD_FAILED:
            Serial.println(F("Feature upload error"));
            break;

        case CANT_ACCEPT_DATA:
            Serial.println(F("Can't accept data"));
            break;

        case IMAGE_UPLOAD_FAILED:
            Serial.println(F("Image upload error"));
            break;

        case TEMPLATE_DELETE_FAILED:
            Serial.println(F("Template delete error"));
            break;

        case EMPTY_DATABASE_FAILED:
            Serial.println(F("Empty database error"));
            break;

        case INCORRECT_PASSWORD:
            Serial.println(F("Incorrect password"));
            break;

        case INCORRECT_BUFFER:
            Serial.println(F("Incorrect buffer"));
            break;

        case FLASH_ERROR:
            Serial.println(F("Flash read/write error"));
            break;

        case INVALID_REGISTER:
            Serial.println(F("Invalid register"));
            break;

        case INVALID_ADDRESS:
            Serial.println(F("Invalid address"));
            break;

        case PASSWORD_NOT_VERIFIED:
            Serial.println(F("Password not verified"));
            break;

        default:
            Serial.println(F("Unknown error"));
            break;
    }
}

response_t FingerPrint::VerifyPassword(void)
{
    uint8_t packet[] = {0x13, U32_TO_ARRAY(__password)};
    uint8_t data[1];

    debug("\nCommand: VerifyPassword\n");

    // Send packet data
    SendPacket(packet, sizeof(packet), OK);

    // Read response from the sensor
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }
    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::SetPassword(uint32_t new_password)
{
    uint8_t packet[] = {0x12, U32_TO_ARRAY(new_password)};
    uint8_t data[1];

    debug("Command: Set password\n");

    // Send packet data
    SendPacket(packet, sizeof(packet), OK);

    // Read response from the sensor
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }
    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::SetAddress(uint32_t new_address)
{
    uint8_t packet[] = {0x15, U32_TO_ARRAY(new_address)};
    uint8_t data[1];
    uint32_t old_address = __address;

    debug("Command: Set address\n");

    // Send packet data
    SendPacket(packet, sizeof(packet), OK);
    __address = new_address;
    // Read response from the sensor
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    } else {
        __address = old_address;
    }
    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::ReadTemplateTable(uint8_t page, uint8_t *table)
{
    uint8_t packet[] = {0x1f, page & 0x03};
    uint8_t data[33];

    debug("Command: Read template table\n");

    // Send packet data
    SendPacket(packet, sizeof(packet), OK);

    // Read response
    if(!ReadPacket(data, 33, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    for(int i = 1; i < 33; i++) {
        table[i-1] = data[i];
    }
    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::ReadTemplateNumber(uint16_t *count)
{
    uint8_t packet[] = {0x1d};
    uint8_t data[3];

    debug("Command: Read template count\n");

    // Send packet data
    SendPacket(packet, sizeof(packet), OK);

    // Read response
    if(!ReadPacket(data, 3, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);

        // Return count of templates
        *count = (data[1] << 8 | data[2]);
    }
    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::GenImage()
{
    uint8_t packet[] = { 0x01 };
    uint8_t data[1];

    debug("Command: Generate image\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::Img2Tz(uint8_t buffer_id)
{
    uint8_t packet[] = { 0x02, buffer_id & 0x3};
    uint8_t data[1];

    debug("Command: Image2Tz\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::RegModel()
{
    uint8_t packet[] = { 0x05 };
    uint8_t data[1];

    debug("Command: Register model\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::StoreModel(uint8_t buffer_id, uint16_t position)
{
    uint8_t packet[] = { 0x06, buffer_id & 0x03, U16_TO_ARRAY(position)};
    uint8_t data[1];

    debug("Command: Store model\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::Empty()
{
    uint8_t packet[] = { 0x0d };
    uint8_t data[1];

    debug("Command: Empty database\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::LoadChar(uint8_t buffer_id, uint16_t position)
{
    uint8_t packet[] = { 0x07, buffer_id & 0x03, U16_TO_ARRAY(position) };
    uint8_t data[1];

    debug("Command: Load characteristic\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::DeleteChar(uint16_t start, uint16_t count)
{
    uint8_t packet[] = { 0x0c, U16_TO_ARRAY(start), U16_TO_ARRAY(count) };
    uint8_t data[1];

    debug("Command: Delete characteristics\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 1, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    return (response_t)data[0];
}

response_t FingerPrint::Match(uint16_t *score)
{
    uint8_t packet[] = { 0x03 };
    uint8_t data[3];

    debug("Command: Match\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 3, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    *score = data[1] << 8 | data[2];
    return (response_t)data[0];
}

response_t FingerPrint::Search(uint8_t buffer_id, uint16_t page, uint16_t count, uint16_t *position, uint16_t *score)
{
    uint8_t packet[] = { 0x04, buffer_id & 0x03, U16_TO_ARRAY(page), U16_TO_ARRAY(count) };
    uint8_t data[5];

    debug("Command: Search\n");

    SendPacket(packet, sizeof(packet), OK);
    if(!ReadPacket(data, 5, ACK)) {
        debug("Status: ");
        if(__verbose)
            PrintResponse(data[0]);
    }

    debug("--------------------------\n");
    *position = data[1] << 8 | data[2];
    *score = data[3] << 8 | data[4];
    return (response_t)data[0];
}
