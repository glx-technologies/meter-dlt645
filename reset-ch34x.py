import usb.core
import usb.util
import sys

# Add the followign udev rules 
# SUBSYSTEM=="usb", ATTRS{idVendor}=="1a86", ATTR{idProduct}="7523", MODE="0666"
#
# To avoid rebooting, execute: 
# udevadm trigger
#

vid = 0x1a86
pid = 0x7523

dev = usb.core.find(idVendor=vid, idProduct=pid)

if dev is None:
  raise valueError('Device not found')

sys.stdout.write('Resetting ...')
dev.reset()
sys.stdout.write('done\n')

