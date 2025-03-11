import streamlit as st
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import datetime
import time
import queue
import math
from sys import platform

# Initialize PortAudio
sd._initialize()

# Set parameters for signal acquisition
eu_sen = np.array([100.0, 100.0])  # Sensitivity in mV per engineering unit (e.g., 100mV/g)
eu_units = ["g", "g"]
blocksize = 1024                  # Number of samples per block
samplerate = 48000                # Sampling rate in Hz

# Function to detect TMS-compatible devices
def TMSFindDevices():
    models = ["485B", "333D", "633A", "SDC0"]
    
    if platform == "win32":  # For Windows
        hapis = sd.query_hostapis()
        api_num = 0
        for api in hapis:
            if api['name'] == "Windows WDM-KS":
                break
            api_num += 1
    else:
        api_num = 0
        
    devices = sd.query_devices()
    dev_info = []
    dev_num = 0
    for device in devices:
        if device['hostapi'] == api_num:
            name = device['name']
            match = next((x for x in models if x in name), False)
            if match:
                loc = name.find(match)
                model = name[loc:loc+6]          # Extract model number
                fmt = name[loc+7:loc+8]            # Extract data format indicator
                serialnum = name[loc+8:loc+14]     # Extract serial number
                if fmt == "2" or fmt == "3":
                    form = 1  # Voltage device
                    sens = [int(name[loc+14:loc+21]), int(name[loc+21:loc+28])]
                    if fmt == "3":  # Format 3 uses 50mV reference; convert to 1V reference
                        sens[0] *= 20
                        sens[1] *= 20 
                    scale = np.array([8388608.0/sens[0],
                                      8388608.0/sens[1]],
                                     dtype='float32')
                    date = datetime.datetime.strptime(name[loc+28:loc+34], '%y%m%d')
                elif fmt == "1":
                    form = 0  # Acceleration device
                    sens = [int(name[loc+14:loc+19]), int(name[loc+19:loc+24])]
                    scale = np.array([855400.0/sens[0],
                                      855400.0/sens[1]],
                                     dtype='float32')
                    date = datetime.datetime.strptime(name[loc+24:loc+30], '%y%m%d')
                else:
                    raise Exception("Expecting 1, 2, or 3 format")
                dev_info.append({"device": dev_num,
                                 "model": model,
                                 "serial_number": serialnum,
                                 "date": date,
                                 "format": form,
                                 "sensitivity_int": sens,
                                 "scale": scale})
        dev_num += 1
    if len(dev_info) == 0:
        raise Exception("No compatible devices found")
    return dev_info

# Detect TMS-compatible device(s)
info = TMSFindDevices()
if len(info) > 1:
    st.write("Using first device found.")
dev = 0

# Set up scaling: if voltage data, adjust using sensor sensitivity; for acceleration, assume scale is correct.
scale = info[dev]['scale']
if info[dev]['format'] == 1:
    for ch in range(len(scale)):
        if eu_sen[ch] != 0.0:
            scale[ch] *= 1.0 / (eu_sen[ch] / 1000.0)

# Function to record signal for a specified duration (in seconds)
def record_signal(record_time):
    total_samples = int(record_time * samplerate)
    num_blocks = math.ceil(total_samples / blocksize)
    all_data = np.empty(total_samples, dtype='float32')
    current_sample_index = 0
    q = queue.Queue()
    
    def callback(indata, frames, time_info, status):
        if status:
            st.write(status)
        q.put(indata.copy())
    
    with sd.InputStream(device=info[dev]['device'], channels=2,
                        samplerate=samplerate, dtype='float32', blocksize=blocksize,
                        callback=callback):
        for i in range(num_blocks):
            data = q.get()  # Get one block (shape: [blocksize, channels])
            sdata = data * scale
            block_data = sdata[:, 0]  # Use channel 0 for display
            remaining = total_samples - current_sample_index
            if remaining < blocksize:
                all_data[current_sample_index:] = block_data[:remaining]
            else:
                all_data[current_sample_index:current_sample_index+blocksize] = block_data
            current_sample_index += blocksize
    all_data = all_data[:total_samples]  # Truncate in case of overshoot
    time_axis = np.linspace(0, record_time, total_samples)
    return time_axis, all_data

# Streamlit UI
st.title("TMS Digital Audio Acquisition on Raspberry Pi")
record_time = st.number_input("Record Duration (seconds):", min_value=1.0, max_value=60.0, value=5.0, step=1.0)

if st.button("Start Recording"):
    with st.spinner("Recording..."):
        t_axis, signal_data = record_signal(record_time)
    # Plot the recorded signal
    fig, ax = plt.subplots()
    ax.plot(t_axis, signal_data)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")
    ax.set_title("Recorded Signal")
    st.pyplot(fig)
    st.success("Recording complete!")
