#!/usr/bin/env python3

import getopt
import time
import dlt645
import sys
from test_dlt645 import *

def change_meter_date(chn, cur_addr, new_date, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- Change meter date ---\n')
    cmd     = [0x01, 0x01, 0x00, 0x04]
    payload = cmd + passwd + opid + list(reversed(new_date))
    chn.encode(cur_addr, 0x14, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x94:
            sys.stdout.write('Date change succeeded (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Date change failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

#--------------------------------------
def _test_main(port_id, cur_addr, new_date, wait_for_read, verbose=0):
    
    rsp = 0
   
    chn=dlt645.Channel(port_id = port_id, tmo_cnt = 10, wait_for_read = wait_for_read)

    if not chn.open():
        sys.stdout.write('Fail to open %s...exit script!\n\n\n' % port_id)
        sys.exit()
    
    if (cur_addr == []):
        rsp = read_meter_address(chn)
    else:
        rsp = is_meter_online(chn, cur_addr)

    if (rsp):
        cur_addr = chn.rx_addr
        rsp = enter_factory_mode(chn, cur_addr, verbose=verbose)

    if (rsp):
        rsp = change_meter_date(chn, cur_addr, new_date, verbose=verbose)
    
    if (rsp):
        rsp = exit_factory_mode(chn, cur_addr, verbose=verbose)
  
    if (rsp):
        rsp = read_date(chn, cur_addr, verbose=verbose)

    sys.stdout.write('\n\n')
    chn.close()

def _show_help():
    sys.stdout.write('arguments for program:\n')
    sys.stdout.write(" -h, --help            : usage help\n")
    sys.stdout.write(" -p, --port            : serial port\n")
    sys.stdout.write(" -c, --meter_address   : 12-digit CURRENT meter ID\n")
    sys.stdout.write(" -n, --new_date        : date in yymmdd\n")
    sys.stdout.write(" -w, --wait            : wait delay before read\n")
    sys.stdout.write(" -v, --verbose         : verbose display\n")

def _main(argv):

    port_id = ''
    cur_addr = []
    new_date = []
    wait_for_read = 0.5
    verbose = 0
    
    sys.stdout.write("\n")
    sys.stdout.write("-----------------------------------------\n")
    sys.stdout.write("---------- Change meter date ------------\n")
    sys.stdout.write("-----------------------------------------\n")

    sys.stdout.write(time.strftime("Run timestamp is " + "%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")

    try:
        opts, args = getopt.getopt(argv,"hp:c:n:w:v",["help", "port=","meter_address=","new_date=","wait=","verbose"])
    except getopt.GetoptError:
        sys.stdout.write("Error in arguments\n")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            _show_help()
            sys.exit()
        elif opt in ("-c", "--meter_address"):
            cur_addr = str_to_bcd_addr(arg)
            if (cur_addr == []):
                sys.stdout.write('\n---> Error in current meter address parsing.\n')
        elif opt in ("-n", "--new_date"):
            new_date = str_to_bcd_date(arg + '00')
            if (new_date == []):
                sys.stdout.write('\n---> Error in new date parsing, so exit script.\n')
                sys.exit()
        elif opt in ("-w", "--wait"):
            wait_for_read = float(arg)
        elif opt in ("-v", "--verbose"):
            verbose = 1
        elif opt in ("-p", "--port"):
            port_id = arg

    def_port = get_def_port()
    
    if port_id == '':
        sys.stdout.write('\n---> No port specified. Use default %s.\n' % def_port)
        #sys.exit()
        port_id = def_port
    
    if new_date == []:
        sys.stdout.write("\n---> No new date specified. Use system date.\n")
        new_date = str_to_bcd_date(time.strftime('%y%m%d', time.localtime())) + [0x00]

    if cur_addr == [] :
        sys.stdout.write("\n---> No current meter address, will use broadcast mode to retrieve.\n")
    
    _test_main(port_id, cur_addr, new_date, wait_for_read, verbose)

if __name__ == "__main__":
    _main(sys.argv[1:])



