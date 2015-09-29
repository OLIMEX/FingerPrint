__author__ = "Stefan Mavrodiev"
__copyright__ = "Copyright 2015, Olimex LTD"
__credits__ = ["Stefan Mavrodiev"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = __author__
__email__ = "support@olimex.com"

import enum


class PacketType(enum.Enum):
    Command = 0x01
    Data = 0x02
    Ack = 0x07
    EndData = 0x08


class ConfirmationCode(enum.Enum):
    OK = 0x00
    receive_error = 0x01
    NoFinger = 0x02
    InputImageFail = 0x03
    ImageMessy = 0x06
    ImageSmall = 0x07
    image_mismatch = 0x08
    DintSearch = 0x09
    MergeFailed = 0x0a
    InvalidPageID = 0x0b
    InvalidTemplate = 0x0c
    execution_failed = 0x0d
    followup_failed = 0x0e
    remove_failed = 0x10
    empty_failed = 0x11
    IncorrectPassword = 0x13
    InvalidImage = 0x15
    write_flash_error = 0x18
