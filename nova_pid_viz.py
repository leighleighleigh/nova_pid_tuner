#!//usr/bin/env python3
# Leigh Oliver, 13 Jan. 2022
# Sorry I didn't document this

import argparse
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

class PIDTuner():
    def __init__(self,args) -> None:
        if(args.pipe):
            self.use_pipe = True
        else:
            self.use_pipe = False

        # Connect to the bus
        if(not self.use_pipe):
            try:
                self.bus = can.interface.Bus(bustype='socketcan', channel=args.device, bitrate=20000)
            except:
                traceback.print_exc()
                sys.exit()

        # Store args
        self.args = args
        self._interval = int((1/float(args.rate))*1000)
        self._terminated = Event()

        # Data to plot
        self._counter = count()
        self.samples_t = []
        self.samples_p = []
        self.samples_v = []

        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Nova Rover PID Viz')
        self.plt.resize(*(640,480))
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'samples', '#')
        self.plt.setYRange(-1,1,padding=0.1)
        self.plt.addLegend()
        self.curvePower = self.plt.plot(self.samples_t, self.samples_p, pen=(255,0,0),name="Power")
        self.curveVelocity = self.plt.plot(self.samples_t, self.samples_v, pen=(0,0,255),name="Velocity")

        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

        # In the background, get our CAN data
        self.start()

        # Start the plot window
        self.app.exec_()

    def updateplot(self):
        self.curvePower.setData(self.samples_t, self.samples_p)
        self.curveVelocity.setData(self.samples_t, self.samples_v)
        self.app.processEvents()     

        # Close on thread stop
        if(self._terminated.isSet()):
            sys.exit()   

    def add_plot_values(self,data : bytearray):
        # Unpack the bytes to a INT16
        powerInt = struct.unpack('>h',data[0:2])[0] 
        velocityInt = struct.unpack('>h',data[2:4])[0] 

        # Normalise them to floats
        powerFloat = float(powerInt) / float(2**15)
        velocityFloat = float(velocityInt) / float(2**15)

        # Add to our data samples
        self.samples_t.append(next(self._counter))
        self.samples_p.append(powerFloat)
        self.samples_v.append(velocityFloat)

    def run(self):
        if(self.use_pipe):
            dataSource = sys.stdin
        else:
            dataSource = self.bus
    
        # Runs continuously getting data
        for msg in dataSource:
            # Crop time window
            self.samples_t = self.samples_t[-self.args.history:]
            self.samples_p = self.samples_p[-self.args.history:]
            self.samples_v = self.samples_v[-self.args.history:]

            # Process messages depending on source
            if(self.use_pipe):
                try:
                    # Split
                    text = msg.rstrip()
                    # Split line on two space gaps
                    lineSplit = text.split("  ")
                    dataString = lineSplit[-1]
                    dataBytes = dataString.split(" ")

                    # Parse each hexadecimal byte into a bytearray
                    data = bytearray()
                    for dB in dataBytes:
                        data.append(int(dB,16))

                    # Now process the message
                    self.add_plot_values(data)
                except:
                    # We did our best
                    print("Failed to parse line: {}".format(msg.rstrip()))
                    pass

            else:
                # Add data
                if(msg.arbitration_id == int(self.args.id,base=16)):
                    # print("got message")
                    msgData = msg.data
                    self.add_plot_values(msgData)

    def start(self):
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
            self._terminated.set()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Nova Rover PID Viz",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('device',type=str,help='The name of the can bus to attach to')
    parser.add_argument('--bitrate',default=20000,type=int,help='The bitrate of the bus')
    parser.add_argument('--id', type=str, default="0x450", help='The (HEX) message ID to plot against')
    parser.add_argument('--history', type=int, default=10000, help='The plot window width in messages')
    parser.add_argument('--rate', type=int, default=10, help='Plot update rate')
    parser.add_argument('--pipe', action='store_true',default=False, help='Get data from candump piped into this tool, rather than a local device')
    args = parser.parse_args()

    tuner = PIDTuner(args)
