# nova_pid_viz
A quick n' dirty python script that plots realtime Power and Velocity CAN messages, for tuning PIDs.
Can be run locally, or can use candump data from file/ssh output!

# Install
It is recommended to install this on the Metabox, and use the pipe-mode to get candump data visualized.
This means the plot graphics don't have to be rendered on-rover.
```bash
git clone https://github.com/leighleighleigh/nova_pid_viz
cd nova_pid_viz
python3 -m pip install -r requirements.txt
```

# Usage
Example for can0 bus
```bash
# For help
python3 nova_pid_viz.py -h 

# (ON-METABOX,RECOMMENDED USE) Get candump data from the rover over ssh, and then visualize it locally
# NOTE: 'vcan0' argument doesnt matter here
# (assumes 'jetson' command to ssh to the rover)
jetson candump vcan0 | python3 nova_pid_viz.py --history 1000 --pipe vcan0

# (ON-ROVER) For a locally running can0 interface with bitrate 20000, id 0x450, history of 1000 messages
python3 nova_pid_viz.py --bitrate 20000 --id 0x450 --history 1000 can0
``` 

# Bonus 
```bash
# Make a virtual (vcan0) can interface on any linux box
sudo apt install can-utils
./virtual_can_setup.sh

# Create some fake data to visualize
./send_dummy_data.sh
```

# Screencap
![Example of the window with flat line example data](./media/screencap.png)
