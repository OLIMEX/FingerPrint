__author__ = "Stefan Mavrodiev"
__copyright__ = "Copyright 2015, Olimex LTD"
__credits__ = ["Stefan Mavrodiev"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = __author__
__email__ = "support@olimex.com"

import Finger

import logging
import argparse
import sys


def parser_hex(value):
    return int(value, 16)

def main():
    # Add epilog
    __epilog = "For suggestions use <" + __email__ + ">"

    # Set program name
    __program = "FingerPrint"

    # Set description
    __description = "Olimex finger sensor demo"

    parser = argparse.ArgumentParser(description=__description,
                                     epilog=__epilog,
                                     prog=__program)

    # Register common arguments
    parser.add_argument("-p", "--port",
                        action="store",
                        required=True,
                        help="Communication port to use")
    parser.add_argument("--baudrate",
                        action="store",
                        type=int,
                        default=57600,
                        help="Set communication speed. Default: 57600")
    parser.add_argument("--settings",
                        action="store_true",
                        help="Read current sensor settings")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enables verbose output")
    parser.add_argument("--version",
                        action="version",
                        version="%(prog)s 0.1.0",
                        help="Print program version")

    # Register common argument group
    sensor_group = parser.add_argument_group("Sensor",
                                             "Sensor configuration")
    sensor_group.add_argument("--set-baud",
                              action="store",
                              type=int,
                              help="Set new speed for the sensor. Range 9600 to 115200")
    sensor_group.add_argument("--password",
                              action="store",
                              type=parser_hex,
                              default=0x00000000,
                              help="Sensor password. Default: 0x00000000")
    sensor_group.add_argument("--address",
                              action="store",
                              type=parser_hex,
                              default=0xFFFFFFFF,
                              help="Sensor address. Default: 0xffffffff")

    # Register argument group
    image_group = parser.add_argument_group("Fingerprint image",
                                            "Actions with ImageBuffer").add_mutually_exclusive_group()
    image_group.add_argument("--download",
                             action="store",
                             help="Download fingerprint image from the sensor")
    image_group.add_argument("--upload",
                             action="store",
                             help="Upload fingerprint image to the sensor")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging

    if args.verbose:
        logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)

    # Start communication with the sensor
    sensor = Finger.System(args.port,
                           baud=args.baudrate,
                           password=args.password,
                           address=args.address)

    # Check is there is someone
    logging.debug("Connecting with sensor")
    logging.debug("----------------------")
    if sensor.verify_password():
        return 1
    else:
        logging.debug("Response: OK")

    # Check if settings flag is set
    if args.settings:
        logging.debug("\nReading settings")
        logging.debug("----------------")
        sensor.read_system_params()
        return 0

    # Check for command
    if args.set_baud:
        logging.debug("\nSetting baudrate to %d" % args.set_baud)
        logging.debug("------------------------------")
        if sensor.set_baudrate(args.set_baud):
            return 1
        else:
            logging.debug("Response: OK")



    print(args)

if __name__ == '__main__':
    main()
