__author__ = "Stefan Mavrodiev"
__copyright__ = "Copyright 2015, Olimex LTD"
__credits__ = ["Stefan Mavrodiev"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = __author__
__email__ = "support@olimex.com"


import serial
import struct

import Errors


class Communication:

    _start_code = 0xEF01

    def __init__(self, port, device_address, baud_rate=57600):

        """
        Class initialization

        :param port: Communication port
        :param device_address: Sensor address
        :param baud_rate: Communication speed
        """
        # Create communication
        self.ser = serial.Serial(port, baudrate=baud_rate, timeout=1)

        # Set current address. May be changed via set and get methods
        self._device_address = device_address

    @property.getter
    def device_address(self):

        """
        Get current address

        :return: Return current device address
        """
        return self._device_address

    @property.setter
    def device_address(self, new_address):

        """
        Set new address for the sensor

        :raise: ValueError on invalid address
        :param new_address: The new address
        """

        # Check new device address
        if new_address > 0xffffffff or new_address < 0:
            raise ValueError("Invalid device address")

        # Set the new address
        self._device_address = new_address

    def send_packet(self, packet, packet_type):

        """
        Send raw packet to sensor

        :param packet: List with bytes to send
        :param packet_type: Packet identification
        :raise Errors.WriteError: If there is problem with sending
        """

        # Create empty byte string
        string = b""

        # Append start code
        buffer = [(self._start_code >> 8 & 0xFF), self._start_code & 0xFF]

        # Append address
        buffer += [(self._device_address >> 24 & 0xFF),
                   (self._device_address >> 16 & 0xFF),
                   (self._device_address >> 8 & 0xFF),
                   (self._device_address >> 0 & 0xFF)]

        # Append packet type
        buffer += [packet_type.value]

        # Append packet len
        packet_len = len(packet)
        buffer += [packet_len + 2 >> 8, packet_len + 2 & 0xFF]

        # Add data packet
        buffer += packet

        # Calculate checksum
        checksum = self.checksum(packet, packet_type)
        buffer += [(checksum >> 8 & 0xFF), checksum & 0xFF]

        # Convert to byte array
        for i in buffer:
            string += struct.pack("B", i)

        # Send packet
        if self.ser.write(string) != len(string):
            raise Errors.WriteError("Not all bytes send")

    def read_packet(self, number_bytes, packet_identification):

        response = self.ser.read(number_bytes)
        checksum = 0

        if len(response) == 0:
            raise Errors.ReadError("Zero bytes read. Check your sensor connection")

        if response[0] != 0xEF or response[1] != 0x01:
            raise Errors.ReadError("Message header doesn't match")

        if response[2] != (self._device_address >> 24 & 0xFF) or \
            response[3] != (self._device_address >> 16 & 0xFF) or \
                response[4] != (self._device_address >> 8 & 0xFF) or \
                response[5] != (self._device_address >> 0 & 0xFF):
            raise Errors.ReadError("Device address doesn't match")

        if response[6] != packet_identification.value:
            raise Errors.ReadError("Packet identification doesn't match")

        checksum = response[6]
        for i in response[7:-2]:
            checksum += i
        if (checksum & 0xFFFF) != (response[-2] << 8 | response[-1]):
            raise Errors.ReadError("Checksum doesn't match.")

        ret = []
        for i in response[9:9 + (response[7] << 8 | response[8]) - 2]:
            ret.append(i)
        return ret

    def checksum(self, packet, packet_type):

        packet_len = len(packet) + 2
        summary = (packet_len >> 8) + (packet_len & 0xFF) + packet_type.value

        for i in packet:
            summary += i

        return summary

