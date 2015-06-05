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

from PIL import Image


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

        # System parameters
        self._packet_size = None
        self._system_id = None
        self._database_size = None
        self._secure_level = None

        # Open serial port
        try:
            self.com = Communication.Communication(port=port, device_address=self._address, baud_rate=baud)
        except IOError as err:
            print(err)
            sys.exit(1)





    def up_image(self):

        sys.stderr.write("Uploading image: ")

        # Form packet
        packet = [0x0a]

        try:
            # Send packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

            # Read the image
            if self.packet_size is None:
                raise Errors.ReadError("Unknown packet size")

                # TODO: Continue from here
        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n" + "\n")
            sys.exit(1)

    def gen_image(self):

        sys.stderr.write("Generating image: ")

        # Form packet
        packet = [0x01]

        try:
            # Send packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n" + "\n")
            sys.exit(1)

    def image_2_tz(self, buffer_id):

        sys.stderr.write("Converting image: ")

        # Form packet
        if buffer_id not in [1, 2]:
            raise Errors.StatusError("Invalid BufferID")

        packet = [0x02, buffer_id]

        try:
            # Send packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n" + "\n")
            sys.exit(1)

    def register_model(self):

        sys.stderr.write("Generating model: ")

        # Form packet
        packet = [0x05]

        try:
            # Send packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n" + "\n")
            sys.exit(1)



    def load_model(self, page_id):

        sys.stderr.write("Load model: ")

        # Form packet
        packet = [0x07, 0x01, page_id >> 8 & 0xFF, page_id & 0xFF]

        try:
            # Send packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n" + "\n")
            sys.exit(1)

    def get_model(self):
        sys.stderr.write("Getting model: ")

        image = []

        packet = [0x0a, 0x01]
        try:
            # Send packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

            sys.stderr.write("Downloading: ")

            for i in range(288):
                if i != 287:
                    data = self.com.read_packet(11 + self.packet_size, StatusCodes.PacketType.Data)
                else:
                    data = self.com.read_packet(11 + self.packet_size, StatusCodes.PacketType.EndData)

                sys.stderr.write("\rDownloading: %.2f" % ((i/287)*100))

                if not data:
                    raise Errors.StatusError("No data")

                image += data

            sys.stderr.write("OK\n")
            self.create_image(image)

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n" + "\n")
            sys.exit(1)


    @staticmethod
    def _u32_to_list(data):
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
    def _16_to_list(data):
        """
        Convert 2-byte integer to list.

        :param data: 2-byte integer
        :return: Converted list
        """
        return [(data >> 8 & 0xFF),
                (data >> 0 & 0xFF)]

    @staticmethod
    def _check_ok(response):
        if response != StatusCodes.ConfirmationCode.OK.value:
            raise Errors.StatusError(Errors.Error.print_error(response))

    @staticmethod
    def convert_image(data):
        new_image = []
        for i in data:
            new_image += [(i & 0xF0), (i & 0x0F) << 4]

        return new_image

    @staticmethod
    def create_image(data):
        img = Image.new('L', (256, 288), 'white')
        data2 = Finger.convert_image(data)

        for y in range(288):
            for x in range(256):
                img.putpixel((x, y), data2[x + (y * 256)])

        img.save("finger.bmp", "BMP")


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
            self._check_ok(ret[0])

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
            self._check_ok(ret[0])
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
        packet = [0x06, buffer_id] + self._16_to_list(page_id)

        try:
            ret = self.com.transfer(packet, 14)
            self._check_ok(ret[0])
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
        packet = [0x0c] + self._16_to_list(start_id) + self._16_to_list(count)

        try:
            self._check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1

    def empty_database(self):
        # Form packet to send
        packet = [0x13]

        try:
            self._check_ok(self.com.transfer(packet, 12)[0])
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
        packet = [0x13] + self._u32_to_list(self._password)

        try:
            self._check_ok(self.com.transfer(packet, 12)[0])
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
        packet = [0x12] + self._u32_to_list(password)

        try:
            self._check_ok(self.com.transfer(packet, 12)[0])
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
        packet = [0x15] + self._u32_to_list(address)

        try:
            self._check_ok(self.com.transfer(packet, 12)[0])
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
            self._check_ok(ret[0])

            self._system_id = ret[3] << 8 | ret[4]
            self._database_size = ret[5] << 8 | ret[6]
            self._secure_level = ret[7] << 8 | ret[8]
            self._packet_size = 32 * pow(2, (ret[13] << 8 | ret[14] + 1))

            sys.stderr.write("Status register 0x%02x\n" % (ret[1] << 8 | ret[2]))
            sys.stderr.write("System ID: 0x%04x\n" % self._system_id)
            sys.stderr.write("Fingerprint database size: %d\n" % self._database_size)
            sys.stderr.write("Security level: %d\n" % self._secure_level)
            sys.stderr.write("Device address: 0x%08x\n" % (ret[9] << 24 | ret[10] << 16 | ret[11] << 8 | ret[12]))
            sys.stderr.write("Packet size: %d bytes\n" % self._packet_size)
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

            self._check_ok(self.com.transfer(packet, 12)[0])
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
            self._check_ok(self.com.transfer(packet, 12)[0])
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
            self._check_ok(self.com.transfer(packet, 12)[0])
            return 0

        except Errors.Error as err:
            sys.stderr.write(err.msg + "\n")
            return 1


