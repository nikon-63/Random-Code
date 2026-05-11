#!/bin/bash 

python3 -m venv .venv --system-site-packages
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install adafruit-blinka adafruit-circuitpython-pn532