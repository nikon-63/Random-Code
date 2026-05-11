import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

URL_TO_WRITE = "https://change-me.com"

CS_PIN = board.D5

NDEF_START_PAGE = 4
PAGE_SIZE = 4


def build_ndef_url_tlv(url: str) -> bytes:
    uri_prefixes = [
        ("http://www.", 0x01),
        ("https://www.", 0x02),
        ("http://", 0x03),
        ("https://", 0x04),
    ]

    prefix_code = 0x00
    uri_body = url

    for prefix, code in uri_prefixes:
        if url.startswith(prefix):
            prefix_code = code
            uri_body = url[len(prefix):]
            break

    uri_payload = bytes([prefix_code]) + uri_body.encode("utf-8")

    if len(uri_payload) > 255:
        raise ValueError("URL is too long for this simple NDEF writer")

    ndef_record = bytes([
        0xD1,
        0x01,
        len(uri_payload),
        0x55,
    ]) + uri_payload

    if len(ndef_record) < 255:
        tlv = bytes([
            0x03,
            len(ndef_record),
        ]) + ndef_record + bytes([0xFE])
    else:
        tlv = bytes([
            0x03,
            0xFF,
            (len(ndef_record) >> 8) & 0xFF,
            len(ndef_record) & 0xFF,
        ]) + ndef_record + bytes([0xFE])

    return pad_to_page_size(tlv)


def pad_to_page_size(data: bytes) -> bytes:
    while len(data) % PAGE_SIZE != 0:
        data += b"\x00"
    return data


def bytes_to_pages(data: bytes):
    for offset in range(0, len(data), PAGE_SIZE):
        yield data[offset:offset + PAGE_SIZE]


def read_bytes(pn532, start_page: int, length: int) -> bytes:
    output = bytearray()
    pages_needed = (length + PAGE_SIZE - 1) // PAGE_SIZE

    for page in range(start_page, start_page + pages_needed):
        block = pn532.ntag2xx_read_block(page)

        if block is None:
            raise RuntimeError(f"Failed to read page {page}")

        output.extend(block)

    return bytes(output[:length])


def wait_for_tag(pn532):
    while True:
        uid = pn532.read_passive_target(timeout=0.25)
        if uid is not None:
            return uid


def wait_for_tag_removed(pn532):
    while True:
        uid = pn532.read_passive_target(timeout=0.25)
        if uid is None:
            return


def get_tag_capacity_bytes(pn532) -> int:
    cc = pn532.ntag2xx_read_block(3)

    if cc is None:
        raise RuntimeError("Could not read Capability Container page 3")

    if cc[0] != 0xE1:
        raise RuntimeError(
            f"Tag does not look NDEF formatted. Page 3 = {cc.hex(' ').upper()}"
        )

    return cc[2] * 8


def flash_tag(pn532, url: str) -> bool:
    expected_data = build_ndef_url_tlv(url)

    capacity = get_tag_capacity_bytes(pn532)

    if len(expected_data) > capacity:
        raise RuntimeError(
            f"NDEF payload is too large: {len(expected_data)} bytes, tag capacity {capacity} bytes"
        )

    print(f"Writing {len(expected_data)} bytes...")

    for index, page_data in enumerate(bytes_to_pages(expected_data)):
        page = NDEF_START_PAGE + index

        ok = pn532.ntag2xx_write_block(page, page_data)

        if not ok:
            raise RuntimeError(f"Failed to write page {page}")

        time.sleep(0.02)

    print("Reading back to verify...")

    actual_data = read_bytes(
        pn532,
        NDEF_START_PAGE,
        len(expected_data),
    )

    if actual_data != expected_data:
        print("Verification failed.")
        print("Expected:", expected_data.hex(" ").upper())
        print("Actual:  ", actual_data.hex(" ").upper())
        return False

    return True


def main():
    print("Starting PN532...")
    print(f"URL to write: {URL_TO_WRITE}")
    print()

    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    cs_pin = DigitalInOut(CS_PIN)

    pn532 = PN532_SPI(spi, cs_pin, debug=False)

    ic, ver, rev, support = pn532.firmware_version
    print(f"Found PN532 firmware version: {ver}.{rev}")

    pn532.SAM_configuration()

    count = 0

    print()
    print("Ready.")
    print("Place a tag on the reader. Remove it after it says DONE.")
    print()

    while True:
        print("Waiting for tag...")

        uid = wait_for_tag(pn532)
        uid_text = uid.hex(":").upper()

        print(f"Detected tag: {uid_text}")

        try:
            success = flash_tag(pn532, URL_TO_WRITE)

            if success:
                count += 1
                print()
                print(f"DONE ✅  Tag flashed and verified. Total done: {count}")
                print("\a")
            else:
                print()
                print("FAILED ❌  Tag written but verification did not match.")
                print("\a\a")

        except Exception as error:
            print()
            print(f"ERROR ❌  {error}")
            print("\a\a")

        print()
        print("Remove tag...")
        wait_for_tag_removed(pn532)

        time.sleep(0.5)
        print()


if __name__ == "__main__":
    main()