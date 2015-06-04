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
    sensor_group.add_argument("--baudrate",
                              action="store",
                              type=int,
                              default=57600,
                              help="Set communication speed. Default: 57600")
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
        logging.basicConfig(format="%(message)s")

    # Start communication with the sensor
    sensor = Finger.Finger(args.port,
                           baud=args.baudrate,
                           password=args.password,
                           address=args.address)

    # Check is there is someone
    logging.info("Connecting with sensor")
    sensor.verify_password()

if __name__ == '__main__':
    main()


# __delay = 3
# a = Finger.Finger()
# a.verify_password()
#
#
# sys.stderr.write("Place your finger on the sensor\n")
# for i in range(__delay):
#     sys.stderr.write("\rTaking image in %d" % (__delay-i))
#     time.sleep(1)
# sys.stderr.write("\n")
# a.gen_image()
# a.get_model()
# sys.exit(0)
#
#
#
# a.image_2_tz(1)
#
# sys.stderr.write("Place your finger one more time the sensor\n")
# for i in range(__delay):
#     sys.stderr.write("\rTaking image in %d" % (__delay-i))
#     time.sleep(1)
# sys.stderr.write("\n")
# a.gen_image()
# a.image_2_tz(2)
# a.register_model()
# a.store_model(0)
# a.load_model(0)