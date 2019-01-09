import dlt645
import sys
from test_dlt645 import *

from flask import Flask, render_template,request, redirect, url_for

app = Flask(__name__)

chn = None
verbose = 1

bat_volt = 0
curr_total_energy = 0
volt = 0

# we are able to make 2 different requests on our webpage
# GET = we just type in the url
# POST = some sort of form submission like a button
@app.route('/', methods = ['POST','GET'])
def hello_world():
    global bat_volt
    global curr_total_energy
    global volt

    # if we make a post request on the webpage aka press button then do stuff
    if request.method == 'POST':

        if request.form['submit'] == 'Load Switch Connect': 
            # read meter address
            rsp = read_meter_address(chn)
            if rsp:
                addr = chn.rx_addr;
                t = time.time() + 60  # valid for 1 min
                dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
                rsp = load_switch_connect(chn, addr, dateline, verbose)
             
        elif request.form['submit'] == 'Load Switch Disconnect': 
            # read meter address
            rsp = read_meter_address(chn)
            if rsp:
                addr = chn.rx_addr;
                t = time.time() + 60  # valid for 1 min
                dateline = str_to_bcd_time(time.strftime('%S%M%H', time.localtime())) +  str_to_bcd_date(time.strftime('%d%m%y', time.localtime()))
                rsp = load_switch_disconnect(chn, addr, dateline, verbose)

        elif request.form['submit'] == 'Read Battery': 
            # read meter address
            rsp = read_meter_address(chn)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_battery_voltage(chn, addr, verbose)
            if rsp:
                p = chn.rx_payload
                bat_volt = '%x.%02x' % (p[-1], p[-2])
        
        elif request.form['submit'] == 'Read Current Month Total Energy': 
            # read meter address
            rsp = read_meter_address(chn)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_energy(chn, addr, 0, 0, verbose)
                curr_total_energy = get_energy_string(chn.rx_payload)

        elif request.form['submit'] == 'Read Voltage': 
            # read meter address
            rsp = read_meter_address(chn)
            if rsp:
                addr = chn.rx_addr;
                rsp = read_voltage(chn, addr, verbose)
                volt = get_voltage_string(chn.rx_payload)
        else:
            pass
    
    # the default page to display will be our template with our template variables
    return render_template('index.html', \
        battery_voltage=bat_volt, \
        current_total_energy=curr_total_energy,\
        voltage=volt)


if __name__ == "__main__":

    port_id = '/dev/ttyUSB1'

    chn=dlt645.Channel(port_id = port_id, tmo_cnt = 10, wait_for_read = 0.5)

    # open the channel
    if not chn.open():
        sys.stdout.write('Fail to open %s...exit script!\n\n\n' % port_id)
        sys.exit()
    
    # lets launch our webpage!
    # do 0.0.0.0 so that we can log into this webpage
    # using another computer on the same network later
    app.run(host='0.0.0.0')
