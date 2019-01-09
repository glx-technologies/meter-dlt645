#!/usr/bin/env python3

import getopt
import time
import dlt645
import sys
import signal
import platform 

from local_keys import *

from serial.tools.list_ports import comports
 
dow = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

def get_def_portx():
    #sys.stdout.write('get_def_port()\n')
    os_name = platform.system();
    #sys.stdout.write('%s\n' % os_name)
    if (os_name == 'Windows'):
        def_port = 'COM1'
    elif (os_name == 'Linux'):
        def_port = '/dev/ttyUSB0'

    return  def_port
    
def get_def_port():
    ports=comports()
    if ports != []:
        return  ports[0].device
    else:
        return None

def signal_handler(signal, frame):
    sys.stdout.write("detected, ending session")
    sys.exit(0)

def is_meter_online(chn, addr, verbose=0):
    sys.stdout.write('\n--- Ping meter %s ---\n' % bcd_to_str_addr(addr))
    chn.encode(addr, 0x13)
    rsp = chn.xchg_data(verbose)
    if rsp:
        sys.stdout.write('Meter status: Online\n')
    else:
        sys.stdout.write('Meter status: Offline\n') 
    return rsp

def enter_factory_mode(chn, addr, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- Enter factory mode ---\n')
    cmd     = [0x0F, 0x01, 0x00, 0x04]
    payload = cmd + passwd + opid + [0x0] 
    chn.encode(addr, 0x14, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x94:
            sys.stdout.write('Enter factory mode success (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Enter factory mode failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

def exit_factory_mode(chn, addr, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- Exit factory mode ---\n')
    cmd     = [0x0F, 0x01, 0x00, 0x04]
    payload = cmd + passwd + opid + [0x1] 
    chn.encode(addr, 0x14, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x94:
            sys.stdout.write('Exit factory mode success (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Exit factory mode failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp
    
def rtcc_write_trim_enable(chn, addr, val, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- RTC Calibration Write Trim Enable ---\n')
    cmd     = [0x8D, 0xF1, 0x00, 0x04]
    payload = cmd + passwd + opid + [val]
    chn.encode(addr, 0x14, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x94:
            sys.stdout.write('Write success (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Write failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

def rtcc_read_trim_enable(chn, addr, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- RTC Calibration Read Trim Enable ---\n')
    cmd     = [0x8D, 0xF1, 0x00, 0x04]
    payload = cmd 
    chn.encode(addr, 0x11, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x91:
            sys.stdout.write('Read success (return code %02x). Trim Enable == %d\n' % (chn.rx_ctrl, chn.rx_payload[-1]))
        else:
            sys.stdout.write('Read failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

def rtcc_write_pulse_source(chn, addr, val, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- RTC Calibration Write Pulse Source ---\n')
    cmd     = [0x9f, 0xF1, 0x00, 0x04]
    payload = cmd + passwd + opid + [val]
    chn.encode(addr, 0x14, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x94:
            sys.stdout.write('Write success (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Write failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

def rtcc_read_pulse_source(chn, addr, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- RTC Calibration Read Pulse Source ---\n')
    cmd     = [0x9f, 0xF1, 0x00, 0x04]
    payload = cmd 
    chn.encode(addr, 0x11, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x91:
            sys.stdout.write('Read success (return code %02x). Pulse source == %d\n' % (chn.rx_ctrl, chn.rx_payload[-1]))
        else:
            sys.stdout.write('Read failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp
    
def rtcc_read_ee_fdiv(chn, addr, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- RTC Calibration Read EE FDIV ---\n')
    cmd     = [0x8F, 0xF1, 0x00, 0x04]
    payload = cmd 
    chn.encode(addr, 0x11, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x91:
            sys.stdout.write('Read success (return code %02x). EE FDIV == 0x%02x%02x\n' % (chn.rx_ctrl, chn.rx_payload[-1], chn.rx_payload[-2]))
        else:
            sys.stdout.write('Read failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

def rtcc_write_ee_fdiv(chn, addr, val, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- RTC Calibration Write EE FDIV ---\n')
    cmd     = [0x8F, 0xF1, 0x00, 0x04]
    payload = cmd + passwd + opid + val
    chn.encode(addr, 0x14, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x94:
            sys.stdout.write('Write success (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Write failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp
    
def load_switch_connect(chn, addr, dateline, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- Load Switch Connect ---\n')
    #payload = passwd + opid + [0x1B, 0x00, 0x22, 0x04, 0x09, 0x26, 0x09, 0x26]
    payload = passwd + opid + [0x1B, 0x00] + dateline
    chn.encode(addr, 0x1C, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x9C:
            sys.stdout.write('Write success (return code %02x).\n' % chn.rx_ctrl)
            sys.stdout.write('Press button for > 3s to connect.\n')
        else:
            sys.stdout.write('Write failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp

def load_switch_disconnect(chn, addr, dateline, verbose=0):
    global passwd
    global opid

    sys.stdout.write('\n--- Load Switch Disconnect ---\n')
    #payload = passwd + opid + [0x1A, 0x00, 0x19, 0x56, 0x08, 0x26, 0x09, 0x26]
    payload = passwd + opid + [0x1A, 0x00] + dateline
    chn.encode(addr, 0x1C, payload)
    rsp = chn.xchg_data(verbose=verbose, retry=0)
    if rsp:
        if chn.rx_ctrl == 0x9C:
            sys.stdout.write('Write success (return code %02x).\n' % chn.rx_ctrl)
        else:
            sys.stdout.write('Write failed (return code %02x).\n' % chn.rx_ctrl)
    return rsp


def read_meter_address(chn, verbose=0):
    sys.stdout.write('\n--- Read meter address with broadcase mode ---\n')
    chn.encode([0xaa]*6, 0x13)
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = ''
        for i in range(-1,-7,-1):
            s = s + '%02x' % p[i]
        sys.stdout.write('Meter address: %s\n' % s)
    return rsp

def read_power(chn, addr, verbose=0):
    # page 53, table A3
    sys.stdout.write('\n--- Read power ---\n')
    chn.encode(addr, 0x11, [0x0, 0x0, 0x3, 0x2])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = "%x%02x%02x" % (p[-1], p[-2], p[-3])
        l = list(s)
        l.insert(-4, '.')
        s = ''.join(l)
        sys.stdout.write("Power: %s kW\n" % s)

    return rsp

def read_voltage(chn, addr, verbose=0):
    # page 53, table A3
    sys.stdout.write('\n--- Read voltage ---\n')
    chn.encode(addr, 0x11, [0x0, 0x1, 0x1, 0x2])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = "%x%02x" % (p[-1], p[-2])
        l = list(s)
        l.insert(-1, '.')
        s = ''.join(l)
        sys.stdout.write("Voltage: %s V\n" % s)

    return rsp

def get_voltage_string(p):
    s = "%x%02x" % (p[-1], p[-2])
    l = list(s)
    l.insert(-1, '.')
    s = ''.join(l)
    return s

def read_current(chn, addr, verbose=0):
    sys.stdout.write('\n--- Read current ---\n')
    chn.encode(addr, 0x11, [0x0, 0x1, 0x2, 0x2])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        
        sg = ''
        if p[-1] >= 0x80:
            p[-1] = p[-1] & 0x7f
            sg = '-'

        if p[-1]:
            s = "%x%02x%02x" % (p[-1], p[-2], p[-3])
        else:
            s = "%02x%02x" % (p[-2], p[-3])

        l = list(s)
        l.insert(-3, '.')
        s = ''.join(l)
        s = sg + s
        sys.stdout.write("Current: %s A\n" %s)

    return rsp

def read_energy(chn, addr, month, segment, verbose=0):
    month_tab = ['Current', 'Last 1', 'Last 2', 'Last 3', \
           'Last 4', 'Last 5', 'Last 6', 'Last 7', \
           'Last 8', 'Last 9', 'Last 10', 'Last 11', 
           'Last 12']

    segment_tab = ['Total', 'Ultra-Peak', 'Peak', 'Normal', 'Trough'] 
    sys.stdout.write('\n--- Read energy (%s Month) ---\n' % month_tab[month])
    chn.encode(addr, 0x11, [month, segment, 0x0, 0x0])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        
        if p[-1]:
            s = "%x%02x%02x%02x" % (p[-1], p[-2], p[-3], p[-4])
        elif p[-2]:
            s = "%x%02x%02x" % (p[-2], p[-3], p[-4])
        else:
            s = "%x%02x" % (p[-3], p[-4])
        
        l = list(s)
        l.insert(-2, '.')
        s = ''.join(l)
        sys.stdout.write("%s: %s kWh\n" % (segment_tab[segment], s))
            
    return rsp

def get_energy_string(p):
    if p[-1]:
        s = "%x%02x%02x%02x" % (p[-1], p[-2], p[-3], p[-4])
    elif p[-2]:
        s = "%x%02x%02x" % (p[-2], p[-3], p[-4])
    else:
        s = "%x%02x" % (p[-3], p[-4])
        
    l = list(s)
    l.insert(-2, '.')
    s = ''.join(l)
    return s

def read_date(chn, addr, verbose=0):
   
    sys.stdout.write('\n--- Read date ---\n')
    chn.encode(addr, 0x11, [0x1, 0x1, 0x0, 0x4])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = '%02x-%02x-%02x %s' % (p[-1], p[-2], p[-3], dow[p[-4]])
        sys.stdout.write('Date: %s\n' % s)
    return rsp

def read_time(chn, addr, verbose=0):
    sys.stdout.write('\n--- Read time ---\n')
    chn.encode(addr, 0x11, [0x2, 0x1, 0x0, 0x4])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = '%02x:%02x:%02x' % (p[-1], p[-2], p[-3])
        sys.stdout.write('Time: %s\n' % s)
    return rsp

#--------------------------------------
def read_temperature(chn, addr, verbose=0):
    sys.stdout.write('\n--- Read temperature ---\n')
    chn.encode(addr, 0x11, [0x07, 0x00, 0x80, 0x02])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        sg = ''
        if p[-1] >= 0x80:
            p[-1] = p[-1] & 0x7f
            sg = '-'

        if p[-1]:
            s = '%x%02x' % (p[-1], p[-2])
        else:
            s = '%02x' % p[-2]
        
        l = list(s)
        l.insert(-1, '.')
        s = ''.join(l)
        s = sg + s
        sys.stdout.write('Temperature: %s degree Celsius\n' % s)
        
    return rsp

def read_battery_voltage(chn, addr, verbose=0):
    sys.stdout.write('\n--- Read battery voltage ---\n')
    chn.encode(addr, 0x11, [0x08, 0x00, 0x80, 0x02])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = '%x.%02x' % (p[-1], p[-2])
        sys.stdout.write('Battery voltage: %s V\n' % s)
    return rsp

def read_line_frequency(chn, addr, verbose=0):
    sys.stdout.write('\n--- Read line frequency ---\n')
    chn.encode(addr, 0x11, [0x02, 0x00, 0x80, 0x02])
    rsp = chn.xchg_data(verbose)
    if rsp:
        if chn.rx_ctrl == 0x91: 
            p = chn.rx_payload
            s = "%x%02x" % (p[-1], p[-2])
            l = list(s)
            l.insert(-2, '.')
            s = ''.join(l)
            sys.stdout.write("Frequency: %s Hz\n" % s)
        else:
            sys.stdout.write('Fail to read frequency.\n')
    return rsp

def read_preset_billing_time(chn, addr, verbose=0):
    sys.stdout.write('\n--- Read preset billing time ---\n')
    chn.encode(addr, 0x11, [0x04, 0x12, 0x00, 0x04])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s = '%02x-%02x %02x:%02x' % (p[-1], p[-2], p[-3], p[-4])
        sys.stdout.write('Last outage timestamp: %s\n' % s)
    return rsp

def read_last_outage_timestamp(chn, addr, index, verbose=0):
    sys.stdout.write('\n--- Read last outage timestamp of N = %d ---\n' % index)
    chn.encode(addr, 0x11, [index, 0x00, 0x11, 0x03])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s1 = '%02x-%02x-%02x %02x:%02x:%02x' % (p[-1], p[-2], p[-3], p[-4], p[-5], p[-6])
        s2 = '%02x-%02x-%02x %02x:%02x:%02x' % (p[-7], p[-8], p[-9], p[-10], p[-11], p[-12])
        sys.stdout.write('Last outage timestamp: %s ----> %s \n' % (s2, s1))
    return rsp

def read_time_change_details(chn, addr, index, verbose=0):
    sys.stdout.write('\n--- Read Time Change Details of N = %d ---\n' % index)
    chn.encode(addr, 0x11, [index, 0x04, 0x30, 0x03])
    rsp = chn.xchg_data(verbose)
    if rsp:
        p = chn.rx_payload
        s3 = '%02x%02x%02x%02x' % (p[-13], p[-14], p[-15], p[-16])
        sys.stdout.write('Op Id = %s\n' % s3)
        s1 = '%02x-%02x-%02x %02x:%02x:%02x' % (p[-1], p[-2], p[-3], p[-4], p[-5], p[-6])
        s2 = '%02x-%02x-%02x %02x:%02x:%02x' % (p[-7], p[-8], p[-9], p[-10], p[-11], p[-12])
        sys.stdout.write('Time: %s ----> %s \n' % (s2, s1))
    return rsp

#--------------------------------------
def _test_main(port_id, addr, wait_for_read=0.5, verbose=0):
    
    rsp = 0

    chn=dlt645.Channel(port_id = port_id, tmo_cnt = 10, wait_for_read = wait_for_read)

    if not chn.open() :
        sys.stdout.write('Fail to open %s...exit script!\n\n\n' % port_id)
        sys.exit()

    if (addr == []):
        rsp = read_meter_address(chn, verbose)
    else:
        #chn.print_hex_list(addr)
        rsp = is_meter_online(chn, addr, verbose)

    if rsp:
        addr = chn.rx_addr
        
    if rsp:
        rsp = read_date(chn, addr, verbose)
        
    if rsp:
        rsp = read_time(chn, addr, verbose)
    
    if rsp:
        rsp = read_voltage(chn, addr, verbose)
        
    if rsp:
        rsp = read_current(chn, addr, verbose)
    
    if rsp:
        rsp = read_power(chn, addr, verbose)
   
    if rsp:
        rsp = read_temperature(chn, addr, verbose)

    if rsp:
        rsp = read_battery_voltage(chn, addr, verbose)
    
    if rsp:
        rsp = read_last_outage_timestamp(chn, addr, 1, verbose)

    if rsp:
        rsp = read_preset_billing_time(chn, addr, verbose)

    m = 0
    for n in range(0,5):
        if rsp:
            rsp = read_energy(chn, addr, m, n, verbose)


    sys.stdout.write('\n\n')

    chn.close()

def _show_help():
    sys.stdout.write('arguments for program:\n')
    sys.stdout.write(" -h, --help    : usage help\n")
    sys.stdout.write(" -p, --port    : serial port\n")
    sys.stdout.write(" -a, --address : 12-digit meter ID\n")
    sys.stdout.write(" -w, --wait    : wait delay before read\n")
    sys.stdout.write(" -v, --verbose : verbose display\n")

# These conversion functions can be made generic (to do)
def str_to_bcd_addr(addr_str):
    r = []
    l = list(addr_str) 
    if len(l) != 12:
        return r
    l = [int(a) for a in l]
    for i in range(0,12,2):
        s = (l[i]<<4) + l[i+1]
        r.append(s)
    return r
        
def bcd_to_str_addr(addr_bcd):
    s = ''
    for i in range(0,6):
        s = s + '%02x' % addr_bcd[i]
    return s

def str_to_bcd_date(date_str):
    #sys.stdout.write("%s\n" % date_str)
    r = []
    l = list(date_str) 
    if len(l) != 6:
        return r
    l = [int(a) for a in l]
    for i in range(0,6,2):
        s = (l[i]<<4) + l[i+1]
        r.append(s)
    return r

def bcd_to_str_date(date_bcd):
    s = ''
    for i in range(0,4):
        s = s + '%02x' % date_bcd[i]
    return s

def str_to_bcd_time(time_str):
    r = []
    l = list(time_str) 
    if len(l) != 6:
        return r
    l = [int(a) for a in l]
    for i in range(0,6,2):
        s = (l[i]<<4) + l[i+1]
        r.append(s)
    return r

def bcd_to_str_time(time_bcd):
    s = ''
    for i in range(0,3):
        s = s + '%02x' % time_bcd[i]
    return s

def _main(argv):

    port_id = ''
    addr = []
    wait_for_read = 0.5
    verbose = 0

    signal.signal(signal.SIGINT, signal_handler)
    sys.stdout.write("\n")
    sys.stdout.write("---------------------------------------\n")
    sys.stdout.write("---------- DLT645 test script ---------\n")
    sys.stdout.write("---------------------------------------\n")

    sys.stdout.write(time.strftime("Run timestamp is " + "%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")

    try:
        opts, args = getopt.getopt(argv,"hp:a:w:v",["help", "port=","address=","wait=","verbose"])
    except getopt.GetoptError:
        sys.stdout.write("Error in arguments\n")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            _show_help()
            sys.exit()
        elif opt in ("-a", "--address"):
            addr = str_to_bcd_addr(arg)
            if (addr == []):
                sys.stdout.write('\n---> Error in meter address parsing.\n')
        elif opt in ("-w", "--wait"):
            wait_for_read = float(arg)
        elif opt in ("-p", "--port"):
            port_id = arg
        elif opt in ("-v", "--verbose"):
            verbose = 1

    def_port =  get_def_port()
    
    if port_id == '':
        sys.stdout.write('\n---> No port specified. Use default %s.\n' % def_port)
        #sys.exit()
        port_id = def_port

    if addr == [] :
        sys.stdout.write("\n---> No meter address, will use broadcast mode to retrieve.\n")

    _test_main(port_id, addr, wait_for_read, verbose)


if __name__ == "__main__":
    _main(sys.argv[1:])


