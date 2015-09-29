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
import time


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

    # Models group
    models_group = parser.add_argument_group("Models",
                                             "Arguments for models usage").add_mutually_exclusive_group()
    models_group.add_argument("--list-models",
                              action="store",
                              type=int,
                              choices=[0, 1, 2, 3],
                              help="Print the usage of model pages")
    models_group.add_argument("--model-store",
                              action="store",
                              type=int,
                              nargs=2,
                              metavar=("BUFFER", "PAGE"),
                              help="Transfer model from buffer# to page#")
    models_group.add_argument("--model-delete",
                              action="store",
                              type=int,
                              nargs=2,
                              metavar=("START", "COUNT"),
                              help="Delete models in the database at START to START+COUNT")
    models_group.add_argument("--model-load",
                              action="store",
                              type=int,
                              nargs=2,
                              metavar=("BUFFER", "PAGE"),
                              help="Load model at #PAGE into #BUFFER")
    models_group.add_argument("--model-upload",
                              action="store",
                              nargs=2,
                              metavar=("BUFFER", "FILE"),
                              help="Transfer the content of #BUFFER to #FILE on the host computer")
    models_group.add_argument("--model-download",
                              action="store",
                              nargs=2,
                              metavar=("BUFFER", "FILE"),
                              help="Transfer the content of #FILE to #BUFFER")
    models_group.add_argument("--model-generate",
                              action="store_true",
                              help="Generate fingerprint image")
    models_group.add_argument("--model-chars",
                              action="store",
                              type=int,
                              choices=[1, 2],
                              metavar="BUFFER",
                              help="Generate characteristics from the image in the ImageBuffer and store it in #BUFFER")
    models_group.add_argument("--model-match",
                              action="store_true",
                              help="Compare models in charBuffer1 and charBuffer2 and look for match")
    models_group.add_argument("--model-search",
                              action="store",
                              type=int,
                              nargs=3,
                              metavar=("BUFFER", "START", "COUNT"),
                              help="Search the database for match to the model stored in #BUFFER")
    models_group.add_argument("--models-count",
                              action="store_true",
                              help="Print current models count")
    models_group.add_argument("--model-register",
                              action="store_true",
                              help="Compare CharBuffer1 with CharBuffer2 and creates model")
    models_group.add_argument("--empty",
                              action="store_true",
                              help="Empty model database")

    # Register common argument group
    sensor_group = parser.add_argument_group("Sensor",
                                             "Sensor configuration")
    sensor_group.add_argument("--set-baud",
                              action="store",
                              type=int,
                              choices=[9600, 19200, 28800, 38400, 48000, 57600, 67200, 76800, 86400, 96000, 115200],
                              help="Set new speed for the sensor. Range 9600 to 115200")
    sensor_group.add_argument("--set-security",
                              action="store",
                              type=int,
                              choices=[1, 2, 3, 4, 5],
                              help="Set security level.")
    sensor_group.add_argument("--set-packet",
                              action="store",
                              type=int,
                              choices=[32, 64, 128, 256],
                              help="Set the length of data packet in bytes")
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
    image_group.add_argument("--image-upload",
                             action="store",
                             metavar="FILE",
                             help="Upload fingerprint image from sensor to host PC")

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

    model = Finger.Models(args.port,
                          baud=args.baudrate,
                          password=args.password,
                          address=args.address)

    image = Finger.Image(args.port,
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

    if args.set_security:
        logging.debug("\nSetting security to %d" % args.set_security)
        logging.debug("------------------------------")
        if sensor.set_security(args.set_security):
            return 1
        else:
            logging.debug("Response: OK")

    if args.set_packet:
        logging.debug("\nSetting packet length to %d" % args.set_packet)
        logging.debug("------------------------------")
        if sensor.set_packet(args.set_packet):
            return 1
        else:
            logging.debug("Response: OK")

    if args.list_models is not None:
        model.get_storage_table(args.list_models)

    if args.models_count:
        model.get_model_count()

    if args.model_store is not None:
        model.store_model(args.model_store[0], args.model_store[1])

    if args.model_delete is not None:
        model.delete_model(args.model_delete[0], args.model_delete[1])

    if args.model_load is not None:
        model.load_model(args.model_load[0], args.model_load[1])

    if args.model_upload is not None:
        sensor.read_system_params()
        model.upload_model(args.model_upload[0], args.model_upload[1])

    if args.model_download is not None:
        sensor.read_system_params()
        model.download_model(args.model_download[0], args.model_download[1])

    if args.model_generate:
        model.generate_model()

    if args.model_chars is not None:
        model.generate_characteristics(args.model_chars)

    if args.model_match:
        model.match_model()

    if args.model_search is not None:
        model.search_model(args.model_search[0], args.model_search[1], args.model_search[2])

    if args.image_upload is not None:
        sensor.read_system_params()
        image.upload_image(args.image_upload[0])

    if args.empty:
        model.empty_database()


if __name__ == '__main__':
    main()
