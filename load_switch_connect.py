#!/usr/bin/env python3

import dlt645
import sys
from test_dlt645 import *

verbose = 1

port_id = '/dev/ttyUSB0'

chn=dlt645.Channel(port_id = port_id, tmo_cnt = 10, wait_for_read = 0.5)

# open the channel
if not chn.open():
    sys.stdout.write('Fail to open %s...exit script!\n\n\n' % port_id)
    sys.exit()

# read meter address
rsp = read_meter_address(chn)

if rsp:
    addr = chn.rx_addr;
    t = time.time() + 60  # valid for 1 min
    dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
    rsp = load_switch_connect(chn, addr, dateline, verbose)

