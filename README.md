# nova_pid_viz
A quick n' dirty python script that plots realtime Power and Velocity CAN messages, for tuning PIDs.
By default will plot `candump` messages that are **piped** (`|`) **into it**, example:
```bash
candump can0 | python3 nova_pid_viz.py
```

This means you can get data over SSH
```bash
# (ON-METABOX,RECOMMENDED USE) Get candump data from the rover over ssh, and then visualize it locally
# (assumes 'jetson' command to ssh to the rover)
jetson candump vcan0 | python3 nova_pid_viz.py
```

It can also be run locally, and will use `python-can` to attach to the local CAN interface:
```bash
python3 nova_pid_viz.py --bitrate 20000 --msg-id 0x450 --device can0
```

See `python3 nova_pid_viz.py -h` for additional usage options.

# Install (for Nova Rover members)
It is recommended to install this on the **Metabox**, and use the default pipe-mode to get candump data from the Rover.
```bash
git clone https://github.com/leighleighleigh/nova_pid_viz
cd nova_pid_viz
# Make a virtual environment
python3 -m venv env
# Enter the virtual environment
source ./env/bin/activate
# Install the requirements
pip install -r requirements.txt
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
