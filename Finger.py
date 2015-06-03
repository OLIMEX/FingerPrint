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
import numpy
from PIL import Image



class Finger:

    def __init__(self, password=0x00000000, address=0xFFFFFFFF):

        self.__password = password
        self.__address = address
        # self.packet_size = None
        self.packet_size = 128

        # Open serial port
        try:
            self.com = Communication.Communication(port="/dev/ttyACM0", device_address=self.__address)
        except IOError as err:
            print(err)
            sys.exit(1)




    @staticmethod
    def __u32_to_list(password):
        return [(password >> 24 & 0xFF),
                (password >> 16 & 0xFF),
                (password >> 8 & 0xFF),
                (password >> 0 & 0xFF)]

    def verify_password(self):
        """
        Verify user password against sensor

        :raise Errors.ReadError: If there is problem with communication
        """
        sys.stderr.write("Password verification: ")

        # Form packet to send
        packet = [0x13] + self.__u32_to_list(self.__password)

        try:
            # Send the packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read the response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n")
            sys.exit(1)

    def set_password(self, password):

        """
        Change current device password

        :param password: New password
        :raise Errors.ReadError: If there is problem with communication
        """
        sys.stderr.write("Changing password to (" + str(hex(password)) + "): ")

        # Form packet to send
        packet = [0x12] + self.__u32_to_list(password)

        try:
            # Send the packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read the response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n")
            sys.exit(1)

    def set_address(self, address):

        sys.stderr.write("Changing address to (" + str(hex(address)) + "): ")

        # Form packet to send
        packet = [0x15] + self.__u32_to_list(address)

        try:
            # Send the packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read the response
            ret = self.com.read_packet(12, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n")
            sys.exit(1)

    def read_system_params(self):

        sys.stderr.write("Reading system parameters: ")

        # Form packet
        packet = [0x0f]

        try:
            # Send the packet
            self.com.send_packet(packet, StatusCodes.PacketType.Command)

            # Read the response
            ret = self.com.read_packet(28, StatusCodes.PacketType.Ack)

            # Is response is not OK raise error
            if ret[0] != 0x00:
                raise Errors.StatusError(Errors.Error.print_error(ret[0]))
            else:
                sys.stderr.write("OK\n")

            print("-------------------")
            print("System ID: 0x%04x" % (ret[1] << 8 | ret[2]))
            print("Fingerprint database: %d" % (ret[3] << 8 | ret[4]))
            print("Storage capacity: %d" % (ret[5] << 8 | ret[6]))
            print("Security level: %d" % (ret[7] << 8 | ret[8]))
            print("Device address: 0x%08x" % (ret[9] << 24 | ret[10] << 16 | ret[11] << 8 | ret[12]))
            print("Packet size: %d bytes" % (32 * pow(2, (ret[13] << 8 | ret[14] + 1))))
            print("Baudrate: %d bps\n" % (ret[15] << 8 | ret[16] * 9600))

            self.packet_size = (32 * pow(2, (ret[13] << 8 | ret[14] + 1)))

        except Errors.Error as err:
            sys.stderr.write("Fail\n")
            sys.stderr.write(err.msg + "\n")
            sys.exit(1)

    # TODO: Add methods for changing baud_rate, packet_size and security_level
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
            sys.stderr.write(err.msg + "\n")
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
            sys.stderr.write(err.msg + "\n")
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
            sys.stderr.write(err.msg + "\n")
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
            sys.stderr.write(err.msg + "\n")
            sys.exit(1)

    def store_model(self, page_id):

        sys.stderr.write("Store model: ")

        # Form packet
        packet = [0x06, 0x01, page_id >> 8 & 0xFF, page_id & 0xFF]

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
            sys.stderr.write(err.msg + "\n")
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
            sys.stderr.write(err.msg + "\n")
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
            sys.stderr.write(err.msg + "\n")
            sys.exit(1)

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
