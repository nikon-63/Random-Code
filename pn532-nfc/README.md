# pn532-nfc

> [!NOTE]  
> The python code is AI generated but tested and working. It was reqired just for a small run of flashing NFC tags for a project, push to git for storage and sharing if ever needed again. The code is not intended for production. 

## Overview

The script is designed for bulk flashing NFC tags. When a compatible NFC tag is placed on the reader, the script detects the tag, writes the configured URL as an NDEF URI record, reads the tag back to verify the write was successful, and then waits for the tag to be removed before processing the next one.

The script is intended for NFC Forum Type 2 tags such as:

| Tag Type | Supported |
|---|---|
| `NTAG213` | Yes |
| `NTAG215` | Yes |
| `NTAG216` | Yes |

The script does not lock the tags, so they can be rewritten later. It is written for the PN532 module using SPI on a Raspberry Pi.

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