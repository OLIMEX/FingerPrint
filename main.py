__author__ = "Stefan Mavrodiev"
__copyright__ = "Copyright 2015, Olimex LTD"
__credits__ = ["Stefan Mavrodiev"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = __author__
__email__ = "support@olimex.com"

import Finger
import time
import sys

__delay = 3
a = Finger.Finger()
a.verify_password()


sys.stderr.write("Place your finger on the sensor\n")
for i in range(__delay):
    sys.stderr.write("\rTaking image in %d" % (__delay-i))
    time.sleep(1)
sys.stderr.write("\n")
a.gen_image()
a.get_model()
sys.exit(0)



a.image_2_tz(1)

sys.stderr.write("Place your finger one more time the sensor\n")
for i in range(__delay):
    sys.stderr.write("\rTaking image in %d" % (__delay-i))
    time.sleep(1)
sys.stderr.write("\n")
a.gen_image()
a.image_2_tz(2)
a.register_model()
a.store_model(0)
a.load_model(0)