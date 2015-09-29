__author__ = "Stefan Mavrodiev"
__copyright__ = "Copyright 2015, Olimex LTD"
__credits__ = ["Stefan Mavrodiev"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = __author__
__email__ = "support@olimex.com"

from StatusCodes import ConfirmationCode


class Error(Exception):
    pass

    @staticmethod
    def print_error(err):
        # 0x01
        if err == ConfirmationCode.receive_error.value:
            return "Packet receive errors"
        # 0x02
        elif err == ConfirmationCode.NoFinger.value:
            return "No finger on the sensor"
        # 0x03
        elif err == ConfirmationCode.InputImageFail.value:
            return "Entry unsuccessful"
        # 0x06
        elif err == ConfirmationCode.ImageMessy.value:
            return "Fingerprint image is too messy"
        # 0x07
        elif err == ConfirmationCode.ImageSmall.value:
            return "Fingerprint image is normal, but the feature points are too few"
        # 0x08
        elif err == ConfirmationCode.image_mismatch.value:
            return "Fingerprints do not match"
        # 0x0a
        elif err == ConfirmationCode.MergeFailed.value:
            return "Merge failed. (The two fingerprints does not belong to the same finger)"
        # 0x0b
        elif err == ConfirmationCode.InvalidPageID.value:
            return "PageID beyond the scope of the fingerprint database"
        # 0x0c
        elif err == ConfirmationCode.InvalidTemplate.value:
            return "Read wrong or template invalid"
        # 0x0d
        elif err == ConfirmationCode.execution_failed.value:
            return "Instruction execution failed"
        elif err == ConfirmationCode.followup_failed.value:
            return "Follow-up package receive error"
        # 0x10
        elif err == ConfirmationCode.remove_failed.value:
            return "Remove template failed"
        # 0x11
        elif err == ConfirmationCode.empty_failed.value:
            return "Empty failed"
        # 0x13
        elif err == ConfirmationCode.IncorrectPassword.value:
            return "Incorrect password"
        # 0x15
        elif err == ConfirmationCode.InvalidImage.value:
            return "Fingerprint image is not valid"
        # 0x18
        elif err == ConfirmationCode.write_flash_error.value:
            return "Write FLASH error"
        else:
            return "Unknown error"


class WriteError(Error):
    def __init__(self, msg):
        self.msg = "Write error: " + msg


class ReadError(Error):
    def __init__(self, msg):
        self.msg = "Read error: " + msg


class StatusError(Error):
    def __init__(self, msg):
        self.msg = "Status error: " + msg

