#!//usr/bin/env python3
# Leigh Oliver, 13 Jan. 2022
# Sorry I didn't document this

import argparse
from cmath import log
from mailbox import linesep
import struct
import sys
import time
import traceback
from threading import Event, Thread
from itertools import count
import can
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys
import logging

class PIDVisualizer():
    def __init__(self,args) -> None:
        
        # Check if we are using piped-input or a real can interface
        if(args.device == "pipe"):
            self.use_pipe = True
            # The 'bus' is just stdin
            self.bus = sys.stdin
        else:
            self.use_pipe = False
            # Attach to the socket can device
            try:
                logging.info("Connecting to device {}".format(args.device))
                self.bus = can.interface.Bus(bustype='socketcan', channel=args.device, bitrate=int(args.bitrate))
            except:
                logging.error("Failed to connect to device {}".format(args.device))
                logging.error("{}".format(traceback.format_exc()))
                # traceback.print_exc()
                sys.exit()

        # Use an Event to handle exit of the multiple threads
        self.event_appTerminated = Event()

        # Store the relevant input arguments
        self.plot_length = args.plot_length
        self.plot_rate = max(1,args.plot_rate) # Slowest is 1Hz
        self.plot_normalized = args.plot_normalized
        self.msg_id = int(args.msg_id,16)
        # Convert the plot_rate into a milliseconds interval
        self.plot_interval = int((1/self.plot_rate)*1000)

        # Data to plot
        self.sample_counter = count()
        self.samples_index = []
        self.samples_power = []
        self.samples_velocity = []
        self.samples_setpoint = []
        self.latestSetpoint = 0

        # PyQtGraph stuff, does all the plotting for us
        self.qt_app = QtGui.QApplication([])
        self.qt_plt = pg.plot(title='Nova Rover PID Viz')
        self.qt_plt.resize(*(640,480))
        self.qt_plt.showGrid(x=True, y=True)
        self.qt_plt.setLabel('left', 'amplitude', 'V')
        self.qt_plt.setLabel('bottom', 'samples', '#')
        self.qt_plt.setYRange(-32000,32000,padding=0.1)
        self.qt_plt.addLegend()

        # The curve objects
        self.curvePower = self.qt_plt.plot(self.samples_index, self.samples_power, pen=(255,0,0),name="Power")
        self.curveVelocity = self.qt_plt.plot(self.samples_index, self.samples_velocity, pen=(0,0,255),name="Velocity")
        self.curveSetpoint = self.qt_plt.plot(self.samples_index, self.samples_setpoint, pen=(0,255,0),name="Setpoint")

        # QTimer, this is just a fancy thread managed by Qt for UI stuff
        self.qt_timer = QtCore.QTimer()
        self.qt_timer.timeout.connect(self.qt_update)
        self.qt_timer.start(self.plot_interval)

        # In a separate Thread, get our CAN data
        self.start_data_thread()

        # Start the plot window
        self.qt_app.exec_()

    def qt_update(self):
        # Called on a timer by the Qt app, and updates our curves from the latest samples
        self.curvePower.setData(self.samples_index, self.samples_power)
        self.curveVelocity.setData(self.samples_index, self.samples_velocity)
        self.curveSetpoint.setData(self.samples_index, self.samples_setpoint)
        self.qt_app.processEvents()

    def add_samples(self,data : bytearray):
        # Unpack the bytes to a INT16
        velocityInt = struct.unpack('<h',data[0:2])[0] 
        powerInt = struct.unpack('<h',data[2:4])[0] 

        # Normalise them to floats
        # if(self.plot_normalized):
            # powerFloat = float(powerInt) / float(2**15)
            # velocityFloat = float(velocityInt) / float(2**15)
        # else:
        # Alternate non-normalised method, where they are just plotted as signed integers
        # powerFloat = float(powerInt)
        # velocityFloat = float(velocityInt)
        # logging.debug("P {},V {}\n".format(powerInt,velocityInt))

        # Add to our data samples
        self.samples_index.append(next(self.sample_counter))
        self.samples_power.append(powerInt)
        self.samples_velocity.append(velocityInt)
        self.samples_setpoint.append(self.latestSetpoint)

    def grab_setpoint(self, data: bytearray):
        self.latestSetpoint = struct.unpack('>h',data[0:2])[0]
        print("setpoint ",self.latestSetpoint)

    def extract_data(self,lineSplit):
        # Get the ID portion of the text
        idString = lineSplit[2]
        idValue = int(idString,16)

        # If we dont match this id, skip this message
        if(idValue != self.msg_id):
            return

        # Get the data portion of the text
        dataString = lineSplit[-1]
        # Split into bytes, which are space-separated
        dataBytes = dataString.split(" ")

        # Parse each hexadecimal byte into a bytearray
        data = bytearray()
        for dB in dataBytes:
            data.append(int(dB,16))

        # Now process the message
        self.add_samples(data)

    def extract_setpoint(self,lineSplit):
        # Get the ID portion of the text
        idString = lineSplit[2]
        idValue = int(idString,16)

        # If we dont match this id, skip this message
        if(idValue != 0x44):
            return
        # else:
            # print("got setpoint!")

        # Get the data portion of the text
        dataString = lineSplit[-1]
        # Split into bytes, which are space-separated
        dataBytes = dataString.split(" ")

        # Parse each hexadecimal byte into a bytearray
        data = bytearray()
        for dB in dataBytes:
            data.append(int(dB,16))

        # Now process the message
        self.grab_setpoint(data)

    def run(self):    
        # Runs continuously getting data
        for msg in self.bus:
            # Crop time window to our history size
            self.samples_index = self.samples_index[-self.plot_length:]
            self.samples_power = self.samples_power[-self.plot_length:]
            self.samples_velocity = self.samples_velocity[-self.plot_length:]
            self.samples_setpoint = self.samples_setpoint[-self.plot_length:]

            # Process messages depending on source
            if(self.use_pipe):
                # Remove carriage return
                text = msg.rstrip()

                try:
                    # Split line on two space gaps
                    lineSplit = text.split("  ")
                    self.extract_data(lineSplit)
                    self.extract_setpoint(lineSplit)                    
                except:
                    # We did our best
                    logging.debug("Failed to parse line: {}".format(text))
                    pass

            else:
                # Get data from a real can interface, easy peasy
                if(msg.arbitration_id == int(self.args.id,base=16)):
                    msgData = msg.data
                    self.add_samples(msgData)

    def start_data_thread(self):
        t = Thread(target=self._bootstrap,name="can_reader")
        t.daemon = True 
        t.start()

    def _bootstrap(self):
        try:
            self.run()
        except:
            traceback.print_exc()
        finally:
            # Sets self terminated to True
            self.event_appTerminated.set()

if __name__ == "__main__":
    # Get arguments from input
    parser = argparse.ArgumentParser(description = "Nova Rover PID Viz",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Default (piped-data) arguments
    parser.add_argument('-m','--msg-id',dest="msg_id", type=str, default="0x450", help='The (hexadecimal) message ID to plot')
    parser.add_argument('-l','--plot-length',dest="plot_length", type=int, default=10000, help='How many messages to show in the plot window')
    parser.add_argument('-r','--plot-rate',dest="plot_rate", type=int, default=30, help='How fast the plot window will be updated')
    parser.add_argument('-n','--plot-normalized',dest="plot_normalized", action='store_true', default=True, help='Normalize the plot values to [-1,1]')

    # Direct (local can interface) arguments
    parser.add_argument('-d','--device',type=str,dest="device",default="pipe",
    help='''
        The CAN device to read messages from, e.g 'can0'.
        If 'pipe', the script will use `candump` text piped into it.
        ''')
    
    parser.add_argument('-b','--bitrate',dest="bitrate",default=20000,type=int,help='The bitrate to use if a real CAN device was specified')
    args = parser.parse_args()

    # Setup logging format
    format = "[%(levelname)s] (%(threadName)-9s) %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    # Start
    app = PIDVisualizer(args)
