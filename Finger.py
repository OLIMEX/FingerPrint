__author__ = "Stefan Mavrodiev"
__copyright__ = "Copyright 2015, Olimex LTD"
__credits__ = ["Stefan Mavrodiev"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = __author__
__email__ = "support@olimex.com"

import Communication
import StatusCodes
import Errors

import sys

# from PIL import Image
import PIL.Image

# System parameters
packet_size = None
system_id = None
database_size = None
secure_level = None


class Finger:
    def __init__(self, port, baud=57600, password=0x00000000, address=0xffffffff):

        """
        Class to control finger sensor
        :param port: Communication port
        :param baud: Communication speed
        :param password: Sensor password
        :param address: Sensor address
        """
        self._password = password
        self._address = address

        # Open serial port
        try:
            self.com = Communication.Communication(port=port, device_address=self._address, baud_rate=baud)
        except IOError as err:
            print(err)
            sys.exit(1)


    @staticmethod
    def u32_to_list(data):
        """
        Convert 4-byte integer to list,
        Byte order is MSB first, LSB last.

        :param data: 4-byte integer
        :return: Converted list
        """
        return [(data >> 24 & 0xFF),
                (data >> 16 & 0xFF),
                (data >> 8 & 0xFF),
                (data >> 0 & 0xFF)]

    @staticmethod
    def u16_to_list(data):
        """
        Convert 2-byte integer to list.

        :param data: 2-byte integer
        :return: Converted list
        """
        return [(data >> 8 & 0xFF),
                (data >> 0 & 0xFF)]

    @staticmethod
    def bytes_to_list(data):
        """
        Convert bytes array to list
        :param data: bytes array
        :return: list with data
        """
        return [x for x in data]

    @staticmethod
    def check_ok(response):
        """
        Check if response is OK
        :param response: Received response code
        :raise Errors.StatusError: If response doesn't match
        """
        if response != StatusCodes.ConfirmationCode.OK.value:
            raise Errors.StatusError(Errors.Error.print_error(response))

    @staticmethod
    def __convert_image(data):
        """
        Convert from 1 byte for 2 pixels to 2 bytes for 2 pixels
        :param data: Input data
        :return: Converter data
        """
        new_image = []
        for i in data:
            new_image += [(i & 0xF0), (i & 0x0F) << 4]

        return new_image

    @staticmethod
    def create_image(data, file):
        """
        Create new bmp file and fill it with the data
        :param data: Image data
        :param file: File name
        """
        img = PIL.Image.new('L', (256, 288), 'white')
        data2 = Finger.__convert_image(data)

        for y in range(288):
            for x in range(256):
                img.putpixel((x, y), data2[x + (y * 256)])

        img.save(file + ".bmp", "BMP")


class Image(Finger):

    def upload_image(self, file):

        """
        Transfer image from ImageBuffer from sensor to host PC

        :param file: Name of the output file
        :return: :raise Errors.StatusError: 0 on success, 1 on error
        """
        image = []

        packet = [0x0a]
        try:
            ret = self.com.transfer(packet, 12)
            self.check_ok(ret[0])
            sys.stderr.write("Downloading: ")

            count = 288 * (256 / packet_size)
            for i in range(count):
                if i != count - 1:
                    data = self.com.read_packet(11 + packet_size // 2, StatusCodes.PacketType.Data.value)
                else:
                    data = self.com.read_packet(11 + packet_size // 2, StatusCodes.PacketType.EndData.value)

                sys.stderr.write("\rDownloading: %.2f " % (i / (count - 1) * 100))

                if not data:
                    raise Errors.StatusError("No data")

                image += data

            sys.stderr.write("OK\n")
            self.create_image(image, file)
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1


class Models(Finger):

    def get_storage_table(self, page):
        """
        Print page usage
        :param page: Number of the page
        :return: 0 for success, 1 for error
        """
        packet = [0x1f, page]

        try:
            ret = self.com.transfer(packet, 44)
            self.check_ok(ret[0])

            # Print usage table
            print("\t15 14 13 12 11 10 9  8  7  6  5  4  3  2  1  0")

            for j in range(1, 33, 2):
                sys.stderr.write("%d\t" % ((j-1)*8))
                for i in range(7, -1, -1):
                    if ret[j+1] & (1 << i):
                        sys.stderr.write("x  ")
                    else:
                        sys.stderr.write(".  ")
                for i in range(7, -1, -1):
                    if ret[j] & (1 << i):
                        sys.stderr.write("x  ")
                    else:
                        sys.stderr.write(".  ")
                sys.stderr.write("\n")

            return 0
        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def get_model_count(self):
        """
        Print current models count

        :return: 0 on success, 1 on error
        """
        packet = [0x1d]
        try:
            ret = self.com.transfer(packet, 14)
            self.check_ok(ret[0])
            sys.stderr.write("Models count: %d\n" % (ret[1] << 8 | ret[2]))
            return 0
        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def store_model(self, buffer_id, page_id):
        """
        Store current model in buffer1 or buffer2 to page address
        :param buffer_id: Current BufferID
        :param page_id: Location
        :return: 0 on success, 1 on error
        """

         # Form packet
        packet = [0x06, buffer_id] + self.u16_to_list(page_id)

        try:
            ret = self.com.transfer(packet, 14)
            self.check_ok(ret[0])
            return 0
        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def delete_model(self, start_id, count):
        """
        Delete models
        :param start_id: Start address
        :param count: Number of models to remove
        :return: 0 on success, 1 of fail
        """
        packet = [0x0c] + self.u16_to_list(start_id) + self.u16_to_list(count)

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def empty_database(self):
        # Form packet to send
        """
        Delete all stored models

        :return: 0 on success, 1 on error
        """
        packet = [0x0d]

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def load_model(self, buffer_id, page_id):

        """
        Load characteristic model into CharBuffer1 or CharBuffer2

        :param buffer_id: BufferID
        :param page_id: Template number
        :return: 0 on success, 1 on error
        """
        packet = [0x07, buffer_id] + self.u16_to_list(page_id)

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def upload_model(self, buffer_id, file):

        """
        Transfer content of buffer into file at the host computer
        :param buffer_id: CharBufferID (1 or 2)
        :param file: Output file
        :return: 0 on success, 1 on error
        """
        packet = [0x08, int(buffer_id)]
        data = []

        try:
            # Run
            ret = self.com.transfer(packet, 12)
            self.check_ok(ret[0])

            # Read data
            xfer_count = 512 // (packet_size // 2)
            for i in range(xfer_count):
                if i != xfer_count - 1:
                    data += self.com.read_packet(packet_size // 2 + 11, StatusCodes.PacketType.Data.value)
                else:
                    data += self.com.read_packet(packet_size // 2 + 11, StatusCodes.PacketType.EndData.value)

            # Write to file
            with open(file, 'wb') as f:
                f.write(bytearray(data))
                f.close()

            return 0
        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def download_model(self, buffer_id, file):

        """
        Transfer file to buffer
        :param buffer_id: Number of char buffer
        :param file: Input file
        :return: 0 on success, 1 on error
        """
        packet = [0x09, int(buffer_id)]

        try:
            # Send command
            ret = self.com.transfer(packet, 12)
            self.check_ok(ret[0])

            # Send data
            xfer_count = 512 // (packet_size // 2)
            with open(file, 'rb') as f:
                for i in range(xfer_count):
                    data = f.read(packet_size // 2)
                    if i != xfer_count-1:
                        self.com.send_packet(self.bytes_to_list(data), StatusCodes.PacketType.Data.value)
                    else:
                        self.com.send_packet(self.bytes_to_list(data), StatusCodes.PacketType.EndData.value)

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def generate_model(self):
        """
        Take fingerprint image

        :return: 0 on success, 1 on error
        """
        packet = [0x01]

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def generate_characteristics(self, buffer_id):
        """
        Generate fingerprint characteristics from the image in ImageBuffer
        :param buffer_id: CharBuffer
        :return: 0 in success, 1 on error
        """
        packet = [0x02, buffer_id]
        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def register_model(self):
        """
        Compare charBuffer1 and charBuffer2 and generate signature model

        :return: 0 on success, 1 on error
        """
        packet = [0x05]
        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0
        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def match_model(self):
        """

        Compare CharBuffer1 and CharBuffer2 for match
        :return:
        """
        packet = [0x03]
        try:
            ret = self.com.transfer(packet, 14)
            self.check_ok(ret[0])

            sys.stderr.write("Score: %d\n" % (ret[1] << 8 | ret[2]))
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def search_model(self, buffer_id, start_page, num_pages):
        """
        Search for matching model in the database
        :param buffer_id: charBuffer number
        :param start_page: Start point in the database
        :param num_pages: Number of elements to search
        :return: 0 on success, 1 on fail
        """
        packet = [0x04, buffer_id] + self.u16_to_list(start_page) + self.u16_to_list(num_pages)

        try:
            ret = self.com.transfer(packet, 16)
            self.check_ok(ret[0])

            sys.stderr.write("Page: %d\n" % (ret[1] << 8 | ret[2]))
            sys.stderr.write("Score: %d\n" % (ret[3] << 8 | ret[4]))
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1


class System(Finger):

    def verify_password(self):
        """
        Verify user password against sensor

        :return: 0 on success, 1 on error
        :raise Errors.ReadError: If there is problem with communication
        """

        # Form packet to send
        packet = [0x13] + self.u32_to_list(self._password)

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def set_password(self, password):
        """
        Change current device password

        :param password: New password
        :return: 0 on success, 1 on error
        :raise Errors.ReadError: If there is problem with communication
        """

        # Form packet to send
        packet = [0x12] + self.u32_to_list(password)

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def set_address(self, address):
        """
        Change current device address

        :param address: New address for the sensor
        :return: 0 on success, 1 on error
        :raise Errors.ReadError:
        """

         # Form packet to send
        packet = [0x15] + self.u32_to_list(address)

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            self.com.device_address = address
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def read_system_params(self):
        """
        Read current system parameters

        :return: 0 on success, 1 on error
        """
        packet = [0x0f]

        try:
            ret = self.com.transfer(packet, 28)
            self.check_ok(ret[0])

            global system_id
            system_id = ret[3] << 8 | ret[4]

            global database_size
            database_size = ret[5] << 8 | ret[6]

            global secure_level
            secure_level = ret[7] << 8 | ret[8]

            global packet_size
            packet_size = 32 * pow(2, (ret[13] << 8 | ret[14] + 1))

            sys.stderr.write("Status register 0x%02x\n" % (ret[1] << 8 | ret[2]))
            sys.stderr.write("System ID: 0x%04x\n" % system_id)
            sys.stderr.write("Fingerprint database size: %d\n" % database_size)
            sys.stderr.write("Security level: %d\n" % secure_level)
            sys.stderr.write("Device address: 0x%08x\n" % (ret[9] << 24 | ret[10] << 16 | ret[11] << 8 | ret[12]))
            sys.stderr.write("Packet size: %d bytes\n" % packet_size)
            sys.stderr.write("Baudrate: %d bps\n" % (ret[15] << 8 | ret[16] * 9600))
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def set_baudrate(self, baudrate):
        """
        Set new baudrate
        :param baudrate: Communication speed
        """
        try:
            # Form packet to send
            packet = [0x0e, 4, baudrate//9600]

            self.check_ok(self.com.transfer(packet, 12)[0])
            # self.com.ser.setBaudrate = baudrate  Fixme: Do I need this?
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def set_security(self, level):
        """
        Set new security level
        :param level: Security level
        :return: 0 on success, 1 on error
        """
        packet = [0x0e, 5, level]

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def set_packet(self, length):

        """
        Set packet length
        :param length:
        :return: 0 on success, 1 on error
        """
        if length == 32:
            code = 0
        elif length == 64:
            code = 1
        elif length == 128:
            code = 2
        else:
            code = 3

        packet = [0x0e, 5, code]

        try:
            self.check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1


