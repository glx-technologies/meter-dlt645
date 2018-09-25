#!/usr/bin/env python3

import getopt
import time
import dlt645
import sys
from test_dlt645 import *

#--------------------------------------
def _test_main(port_id, cur_addr, wait_for_read, verbose=0):
    
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

    sys.stdout.write('\n\n')
    chn.close()

def _show_help():
    sys.stdout.write('arguments for program:\n')
    sys.stdout.write(" -h, --help            : usage help\n")
    sys.stdout.write(" -p, --port            : serial port\n")
    sys.stdout.write(" -c, --meter_address   : 12-digit CURRENT meter ID\n")
    sys.stdout.write(" -w, --wait            : wait delay before read\n")
    sys.stdout.write(" -v, --verbose         : verbose display\n")

def _main(argv):

    port_id = ''
    cur_addr = []
    wait_for_read = 0.5
    verbose = 0
    
    sys.stdout.write("\n")
    sys.stdout.write("-----------------------------------------\n")
    sys.stdout.write("---------- Enter factory mode -----------\n")
    sys.stdout.write("-----------------------------------------\n")

    sys.stdout.write(time.strftime("Run timestamp is " + "%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")

    try:
        opts, args = getopt.getopt(argv,"hp:c:w:v",["help", "port=","meter_address=","wait=","verbose"])
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
    
    if cur_addr == [] :
        sys.stdout.write("\n---> No current meter address, will use broadcast mode to retrieve.\n")
    
    _test_main(port_id, cur_addr, wait_for_read, verbose)

if __name__ == "__main__":
    _main(sys.argv[1:])



