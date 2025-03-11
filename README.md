# TMS Digital Audio Acquisition for Raspberry Pi

A Streamlit-based application for capturing and visualizing data from TMS digital audio accelerometers and voltage sensors.

## Overview

This application provides a simple web interface for recording and visualizing signal data from TMS-compatible devices connected to a Raspberry Pi (or other systems). It automatically detects compatible TMS devices, handles the proper scaling of measurements, and displays the recorded signal in real-time.

## Features

- Automatic detection of TMS-compatible devices (models 485B, 333D, 633A, SDC0)
- Support for both acceleration and voltage measurement devices
- Automatic scaling based on device calibration and engineering units
- Configurable recording duration
- Real-time visualization of recorded signals
- Cross-platform support (optimized for Raspberry Pi)

## Prerequisites

- Python 3.6 or higher
- Raspberry Pi (recommended) or any computer with compatible audio inputs
- TMS-compatible sensor device

## Installation

1. Clone this repository or download the script
2. Install required dependencies:

```bash
pip install streamlit numpy sounddevice matplotlib
```

## Usage

1. Connect your TMS-compatible sensor to your Raspberry Pi
2. Run the Streamlit application:

```bash
streamlit run TMS_Digital_Audio_Streamlit.py
```

3. Open the provided URL in your web browser (typically http://localhost:8501)
4. Set the desired recording duration
5. Click "Start Recording" to begin data acquisition
6. View the visualized signal after recording completes

## Supported Devices

This application automatically detects and configures TMS devices with the following format patterns:

- Format 1: Acceleration devices
- Format 2: Voltage devices (1V reference)
- Format 3: Voltage devices (50mV reference, automatically converted to 1V reference)

The application extracts the following information from the device name:
- Model number
- Data format
- Serial number
- Calibration date
- Channel sensitivities

## Technical Details

- Default sample rate: 48000 Hz
- Block size: 1024 samples
- Default engineering unit sensitivity: 100.0 mV/g

## Troubleshooting

- If no devices are detected, ensure your TMS device is properly connected
- On Windows, the application will search for devices using the Windows WDM-KS API
- On other platforms, it will use the default audio API

## Extending

You can modify the following parameters in the code:

- `eu_sen`: Sensitivity in mV per engineering unit
- `eu_units`: Labels for engineering units
- `blocksize`: Number of samples per block
- `samplerate`: Sampling rate in Hz
