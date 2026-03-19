#!/bin/ash
if [ -n "$RTL_SERIAL" ]; then
    DEVICE_ARG="-d:$RTL_SERIAL"
fi
/usr/local/bin/rtl_433 $DEVICE_ARG -Fjson -Ccustomary -R40 | python3 /home/yats/temp_simplified.py