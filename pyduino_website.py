from flask import Flask, render_template,request, redirect, url_for
from pyduino import *
import time
import sys

app = Flask(__name__)

# initialize connection to Arduino
# if your arduino was running on a serial port other than '/dev/ttyACM0/'
# declare: a = Arduino(serial_port='/dev/ttyXXXX')
a = Arduino() 
time.sleep(3)

sys.stdout.write('Arduino initialized')
sys.stdout.flush()

# we are able to make 2 different requests on our webpage
# GET = we just type in the url
# POST = some sort of form submission like a button
@app.route('/', methods = ['POST','GET'])
def hello_world():

    # variables for template page (templates/index.html)
    author = "Kyle"

    # if we make a post request on the webpage aka press button then do stuff
    if request.method == 'POST':

        # if we press the turn on button
        if request.form['submit'] == 'Turn On': 
            sys.stdout.write('TURN ON\n')
            sys.stdout.flush()

            # turn on LED on arduino
            a.led_on()

        # if we press the turn off button
        elif request.form['submit'] == 'Turn Off': 
            sys.stdout.write('TURN OFF\n')
            sys.stdout.flush()

            # turn off LED on arduino
            a.led_off()
        
        elif request.form['submit'] == 'Val Inc':
            sys.stdout.write('Val Inc\n')
            sys.stdout.flush()
            a.val_inc()

        elif request.form['submit'] == 'Val Dec':
            sys.stdout.write('Val Dec\n')
            sys.stdout.flush()
            a.val_dec()

        else:
            pass
    
    # read in analog value from photoresistor
    readval = a.val_read()

    # the default page to display will be our template with our template variables
    return render_template('index.html', author=author, value=readval)


# unsecure API urls
@app.route('/turnon', methods=['GET'] )
def turn_on():
    # turn on LED on arduino
    a.led_on()
    return redirect( url_for('hello_world') )


@app.route('/turnoff', methods=['GET'] )
def turn_off():
    # turn off LED on arduino
    a.led_off()
    return redirect( url_for('hello_world') )



if __name__ == "__main__":

    # lets launch our webpage!
    # do 0.0.0.0 so that we can log into this webpage
    # using another computer on the same network later
    app.run(host='0.0.0.0')
