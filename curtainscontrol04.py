# MQTT client class to subscribe to a feed and drive a motor to control closing and opening curtains

# Import standard python modules.

import sys
import os
import json
import datetime
import time

# import RPi.GPIO as GPIO   # commented out until working on RPi
# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

# GPIO.setmode(GPIO.BCM) commented out until working on RPi

# Set to your Adafruit IO key & username below.
ADAFRUIT_IO_USERNAME = 'hughwright'
ADAFRUIT_IO_KEY = '###'
# See https://accounts.adafruit.com to find your username

# Set to the ID of the feed to subscribe to for updates.
FEED_ID1 = 'Curtains'


#########need to change these once have motor and motor control board to drive motor
#GPIO.setup(23, GPIO.OUT)
#GPIO.output(23, GPIO.LOW)
#GPIO.setup(2, GPIO.OUT)
#GPIO.output(2, GPIO.LOW)

class Curtains(object):
    def __init__(self):
        self.name = None
        self.closed = 0             #default unless curtains_data file exists
        self.time_to_close = 30     #defaults unless curtains_data file exists

    def close_curtains(self, payload):    
        filename = 'C:/Users/hughg/Dropbox/IoT projects/Curtains/curtains_data.json'          
                #####################################
                # you need to change directory path #
                # in above filename to match your system              #
                #####################################
        if not os.path.isfile(filename):        
            # file does not exist, needs creating with default values
            f = open(filename, 'w+')            # create file
            f.close()

            default_data = {                  # set default values
                'status': 0,
                'time_to_close': 30
                # need to time how long your curtains will take to fully close/open 
                # and update time_to_close appropriately. Value is in seconds
            }

            with open(filename, 'w') as f:     # write default values to file
                json.dump(default_data, f)
                current_data = default_data
                print('new file contents = ', current_data)

        else:       
            #file exists so read values from file
            with open(filename, 'r') as f:
                current_data = json.load(f)
                print('existing file contents = ', current_data)

        motor_run_time = (int(payload) - (current_data['status']))*(current_data['time_to_close'])/100

        if motor_run_time > 0:
            print('CCW high')   #set_pin_CCW_high    #set AIN1 Pin to high voltage 
            print('Curtains closing to', payload, 'percent')
            print('motor run time', motor_run_time)
            time.sleep(motor_run_time)
            print('Curtains closed to ', payload, '%')
            print('CCW pin low')   #set_pin_CCW_low     #set AIN1 Pin to low voltage

        elif motor_run_time < 0:
            print('CW pin high')    #set_pin_CW_high     #set AIN2 Pin to high voltage 
            print('Curtains opening to', payload, 'percent')
            print('motor run time', motor_run_time)
            time.sleep(-motor_run_time)
            print('Curtains closed to ', payload, '%')
            print('CW pin low')     # set_pin_CW_low      #set AIN2 Pin to low voltage
        
        else:
            print('Curtains not moved')

        # the above should really have some error checking to make sure curtains have moved
        # and exception handling if not

        current_data['status'] = int(payload)   # updated with new position
      
        with open(filename, 'w') as f:
            json.dump(current_data, f)

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print("Connected to Adafruit IO!  Listening for", FEED_ID1, "changes...", time.strftime("%H:%M:%S", time.localtime()) + '.%d' % (time.time() % 1 * 1000))

    # Subscribe to changes on a feed FEED_ID1.
    client.subscribe(FEED_ID1)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print ("Disconnected from Adafruit IO!", time.strftime("%H:%M:%S", time.localtime()) + '.%d' % (time.time() % 1 * 1000))
    sys.exit(1)


def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print("Feed", feed_id, "received new value:", payload)
    if feed_id == "Curtains":
        curtains1 = Curtains()
        curtains1.close_curtains(payload)

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

# Connect to the Adafruit IO server.
client.connect()

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  
client.loop_blocking()