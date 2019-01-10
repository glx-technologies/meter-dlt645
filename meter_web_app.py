import dlt645
import sys
from test_dlt645 import *

from flask import Flask, render_template,request, redirect, url_for

app = Flask(__name__)


port_id = '/dev/ttyUSB0'

chn=dlt645.Channel(port_id = port_id, tmo_cnt = 10, wait_for_read = 0.5)

# open the channel
if not chn.open():
    sys.stdout.write('Fail to open %s...exit script!\n\n\n' % port_id)
    sys.exit()
    
verbose = 1

battery = '0'
energy = '0'
voltage = '0'
current = '0'
power = '0'
meter_date = ' '
meter_time = ' ' 
temperature = '0'
meter_address = '000000000000'
meter_address_bcd = [(0x0)*6]

# we are able to make 2 different requests on our webpage
# GET = we just type in the url
# POST = some sort of form submission like a button
@app.route('/', methods = ['POST','GET'])
def index():
    global battery
    global energy
    global voltage
    global current
    global power
    global meter_date
    global meter_time
    global temperature
    global meter_address
    global meter_address_bcd

    page = 0

    # if we make a post request on the webpage aka press button then do stuff
    if request.method == 'POST':

        if request.form['submit']== 'Set Meter Address':
            tmp_meter_address = request.form['address']
            if len(tmp_meter_address) == 12:
                meter_address = tmp_meter_address
                meter_address_bcd = str_to_bcd_addr(meter_address)
                sys.stdout.write("%s\n" % bcd_to_str_addr(meter_address_bcd))
                sys.stdout.flush()

        elif request.form['submit'] == 'Read Battery': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_battery_voltage(chn, addr, verbose)
            if rsp:
                battery = get_battery_voltage_string(chn.rx_payload)
        
        elif request.form['submit'] == 'Read Date': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_date(chn, addr, verbose)
            if rsp:
                meter_date = get_date_string(chn.rx_payload)
        
        elif request.form['submit'] == 'Read Time': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_time(chn, addr, verbose)
            if rsp:
                meter_time = get_time_string(chn.rx_payload)
        
        elif request.form['submit'] == 'Read Temperature': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_temperature(chn, addr, verbose)
            if rsp:
                temperature = get_temperature_string(chn.rx_payload)

        elif request.form['submit'] == 'Read Energy': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_energy(chn, addr, 0, 0, verbose)
            if rsp:
                energy = get_energy_string(chn.rx_payload)

        elif request.form['submit'] == 'Read Voltage': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_voltage(chn, addr, verbose)
            if rsp:
                voltage = get_voltage_string(chn.rx_payload)
        
        elif request.form['submit'] == 'Read Current': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_current(chn, addr, verbose)
            if rsp:
                current = get_current_string(chn.rx_payload)
        
        elif request.form['submit'] == 'Read Power': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_power(chn, addr, verbose)
            if rsp:
                power = get_power_string(chn.rx_payload)
        
        elif request.form['submit'] == 'Load Switch': 
            page = 1
        
        elif request.form['submit'] == 'Load Switch Connect': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                sys.stdout.write('2')
                sys.stdout.flush()
                addr = chn.rx_addr;
                rsp = enter_factory_mode(chn, addr, verbose)
                t = time.time() + 60  # valid for 1 min
                dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
                rsp = load_switch_connect(chn, addr, dateline, verbose)
                 
        elif request.form['submit'] == 'Load Switch Disconnect': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                sys.stdout.write('2')
                sys.stdout.flush()
                addr = chn.rx_addr;
                rsp = enter_factory_mode(chn, addr, verbose)
                t = time.time() + 60  # valid for 1 min
                dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
                rsp = load_switch_disconnect(chn, addr, dateline, verbose)
        else:
            pass
   
    if page == 1:
        return render_template('load_switch.html')

    else:
        # the default page to display will be our template with our template variables
        return render_template('index.html', \
            battery=battery, \
            meter_address=meter_address,\
            meter_date=meter_date,\
            meter_time=meter_time,\
            temperature=temperature,\
            energy=energy,\
            voltage=voltage,\
            current=current, \
            power=power)

@app.route('/load_switch', methods = ['POST','GET'])
def load_switch():
    if request.method == 'POST':
        if request.form['submit'] == 'Load Switch Connect': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                sys.stdout.write('2')
                sys.stdout.flush()
                addr = chn.rx_addr;
                rsp = enter_factory_mode(chn, addr, verbose)
                t = time.time() + 60  # valid for 1 min
                dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
                rsp = load_switch_connect(chn, addr, dateline, verbose)
                 
        elif request.form['submit'] == 'Load Switch Disconnect': 
            rsp = is_meter_online(chn, meter_address_bcd, verbose)
            if rsp:
                sys.stdout.write('2')
                sys.stdout.flush()
                addr = chn.rx_addr;
                rsp = enter_factory_mode(chn, addr, verbose)
                t = time.time() + 60  # valid for 1 min
                dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
                rsp = load_switch_disconnect(chn, addr, dateline, verbose)
        else:
            pass

    return render_template('load_switch.html')

if __name__ == "__main__":
    # lets launch our webpage!
    # do 0.0.0.0 so that we can log into this webpage
    # using another computer on the same network later
    app.run(host='0.0.0.0', debug=True)
