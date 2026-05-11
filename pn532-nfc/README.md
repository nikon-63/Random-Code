# pn532-nfc

## Overview


## Setup
1. Enable SPI on Raspberry Pi (Interface Options > SPI)
```bash
sudo raspi-config
```

2. Connect the PN532 NFC module to the Raspberry Pi.
Set PN532 board to **SPI mode**:

| PN532 Mode Pin | Setting |
|---|---|
| `SEL0` | `OFF` |
| `SEL1` | `ON` |

Wire PN532 board to Raspberry Pi:

| PN532 Pin | Raspberry Pi Physical Pin | Raspberry Pi GPIO |
|---|---:|---|
| `3.3V` | Pin `1` | `3.3V` |
| `GND` | Pin `6` | `GND` |
| `MOSI` | Pin `19` | `GPIO10 / SPI0 MOSI` |
| `MISO` | Pin `21` | `GPIO9 / SPI0 MISO` |
| `SCK` | Pin `23` | `GPIO11 / SPI0 SCLK` |
| `SSEL` | Pin `29` | `GPIO5` |


3. Install dependencies
```bash
sudo apt update
sudo apt install -y python3-venv python3-libgpiod libgpiod2

./setup.sh
```

4. Set URL
Edit the main.py file and set the URL to which the NFC tag data will be sent:
```python
URL_TO_WRITE = "http://example.com/nfc-data"
```

5. Run script
```bash
source .venv/bin/activate
python3 main.py
```