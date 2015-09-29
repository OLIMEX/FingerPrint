# Description
Demo program for SNS-FINGERPRINT module.

In OLinuXino folder there is code for OLinuXino boards written in Python, tested on A20-OLinuXino-MICRO.

In Arduino folder there is code for OLIMEXINO-32U4.

ESP8266 JavaScript Firmware also recognizes this module as Plug-and-Play and senses when it's attached to ESP8266-EVB.

With this demo program you can almost fully control this module - taking image of fingerprint, creating
characteristics of it, store it in database, search for it and etc. 

The OLinuXino demo is written on Python3.


# Requirements
* python3
* pillow
* pyserial

# Usage
See help for detailed usage
```sh
python3 main.py
python3 main.py --help
```
