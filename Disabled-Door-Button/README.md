# Disabled Door Button

## Overview

This is a small Python project I have been meaning to make for a while. It listens for button presses from an old disabled access “press to open” door button that contains a Larco 433 MHz door control transmitter.

The Larco documentation states that these transmitters operate at **433.92 MHz** and use **code hopping** for secure activations:

https://drive.google.com/file/d/1AWbtjNSeH1lx_TxamcBDGBF6SvHMgVWw/view

While testing, I got codes like this:

```text
3CAC705B F4BAD8BB8
D651F04F F4BAD8BB8
DEDD2502 F4BAD8BB8
48C6F3BF F4BAD8BB8
```

The first part changes because of the rolling/code-hopping system, but the suffix stays static. This script is based on looking for the static suffix.

Later on, I would like to look into the enrollment/linking process between the transmitter and the receiver to see if I can incorporate more of it into this script.

## Install

Install the dependencies. This has only been tested on a Raspberry Pi 5.

```bash
sudo apt install -y rtl-sdr librtlsdr-dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

Run the script:

```bash
python3 main.py
```

## Notes

This script is designed to stay simple. The main script imports the listener class, as i reuse it in other projects to link it to Home Assistant.
