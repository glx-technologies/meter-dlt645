#!/usr/bin/env python3

import serial
import time
import sys
import platform

from local_keys import *

ser =  serial.Serial()

ser.port = '/dev/ttyUSB0'
ser.baudrate = 2400
ser.parity = serial.PARITY_EVEN

try:
    ser.open()
    sys.stdout.write('%s access ok.\n' % (ser.port))
except serial.SerialException:
    sys.stdout.write('%s access fail.\n' % (ser.port))
    sys.exit()

tx_frame =  [0xfe, 0xfe, 0x68]
tx_frame += [0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa]
tx_frame += [0x68, 0x13, 0x00]
tx_frame += [0xdf, 0x16]

sys.stdout.write('TX: ')
for x in tx_frame:
    sys.stdout.write('%02x ' % (x))

sys.stdout.write('\n');

tx_bytes = bytearray(tx_frame)

ser.write(tx_bytes)

time.sleep(1)

rx_bytes = bytearray(ser.read(ser.inWaiting()))
rx_frame = [c for c in rx_bytes]

sys.stdout.write('RX: ')
for x in rx_frame:
    sys.stdout.write('%02x ' % (x))

sys.stdout.write('\n');
ser.close()
