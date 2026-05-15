import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

import numpy as np
from rtlsdr import RtlSdr


@dataclass
class RFFrame:
    frame_hex: str
    bits: str
    timestamp: datetime


class RFButtonListener:
    def __init__(
        self,
        target_suffix: str,
        on_press: Optional[Callable[[RFFrame], None]] = None,
        frequency: float = 433.92e6,
        sample_rate: int = 1_000_000,
        gain: str = "auto",
        chunk_size: int = 256 * 1024,
        expected_bits: int = 65,
        cooldown_seconds: float = 2.0,
        threshold_multiplier: float = 3.0,
        min_pulse_us: int = 80,
        max_pulse_us: int = 20_000,
        packet_gap_us: int = 3000,
        min_packet_pulses: int = 40,
        min_high_pulses: int = 10,
        debug: bool = False,
    ):
        self.target_suffix = target_suffix.upper()
        self.on_press = on_press

        self.frequency = frequency
        self.sample_rate = sample_rate
        self.gain = gain
        self.chunk_size = chunk_size

        self.expected_bits = expected_bits
        self.cooldown_seconds = cooldown_seconds

        self.threshold_multiplier = threshold_multiplier
        self.min_pulse_us = min_pulse_us
        self.max_pulse_us = max_pulse_us
        self.packet_gap_us = packet_gap_us
        self.min_packet_pulses = min_packet_pulses
        self.min_high_pulses = min_high_pulses

        self.debug = debug

        self.last_trigger_time = 0.0
        self.sdr = None

    def listen(self):
        self.sdr = RtlSdr()
        self.sdr.sample_rate = self.sample_rate
        self.sdr.center_freq = self.frequency
        self.sdr.gain = self.gain

        try:
            while True:
                samples = self.sdr.read_samples(self.chunk_size)
                self.process_samples(samples)

        except KeyboardInterrupt:
            print()
            print("Stopping RF listener.")

        finally:
            self.close()

    def close(self):
        if self.sdr is not None:
            self.sdr.close()
            self.sdr = None

    def process_samples(self, samples):
        digital = self.iq_to_digital(samples)
        pulses = self.digital_to_pulses(digital)
        packets = self.split_packets(pulses)

        for packet in packets:
            if self.looks_like_packet(packet):
                self.process_packet(packet)

    def iq_to_digital(self, samples):
        envelope = np.abs(samples)

        noise_floor = np.median(envelope)
        threshold = noise_floor * self.threshold_multiplier

        return envelope > threshold

    def digital_to_pulses(self, digital):
        pulses = []

        last_level = bool(digital[0])
        count = 1

        for value in digital[1:]:
            level = bool(value)

            if level == last_level:
                count += 1
                continue

            duration_us = count / self.sample_rate * 1_000_000

            if duration_us >= self.min_pulse_us:
                self._append_or_merge_pulse(pulses, last_level, duration_us)

            last_level = level
            count = 1

        duration_us = count / self.sample_rate * 1_000_000

        if duration_us >= self.min_pulse_us:
            self._append_or_merge_pulse(pulses, last_level, duration_us)

        return pulses

    @staticmethod
    def _append_or_merge_pulse(pulses, level, duration_us):
        if pulses and pulses[-1][0] == level:
            old_level, old_duration = pulses[-1]
            pulses[-1] = (old_level, old_duration + duration_us)
        else:
            pulses.append((level, duration_us))

    def split_packets(self, pulses):
        packets = []
        current = []

        for level, duration in pulses:
            if level is False and duration >= self.packet_gap_us:
                if current:
                    packets.append(current)
                    current = []
                continue

            if duration <= self.max_pulse_us:
                current.append((level, duration))

        if current:
            packets.append(current)

        return packets

    def looks_like_packet(self, packet):
        if len(packet) < self.min_packet_pulses:
            return False

        high_count = sum(1 for level, _ in packet if level)

        if high_count < self.min_high_pulses:
            return False

        return True

    def process_packet(self, packet):
        bits = self.decode_packet(packet)

        if "?" in bits:
            if self.debug:
                print("Ignored packet: damaged symbol pair")
            return

        if len(bits) != self.expected_bits:
            if self.debug and len(bits) > 20:
                print(f"Ignored partial frame: {len(bits)} bits")
            return

        frame_hex = self.bits_to_hex(bits)

        if frame_hex is None:
            return

        if self.debug:
            print(f"Valid {self.expected_bits}-bit frame seen: {frame_hex}")

        self.handle_frame(frame_hex, bits)

    def decode_packet(self, packet):
        symbols = [
            self.pulse_to_symbol(level, duration)
            for level, duration in packet
        ]

        bits = []

        i = 0

        while i + 1 < len(symbols):
            pair = (symbols[i], symbols[i + 1])

            if pair == ("HL", "LS"):
                bits.append("1")
            elif pair == ("HS", "LL"):
                bits.append("0")
            else:
                bits.append("?")

            i += 2

        return "".join(bits)

    def pulse_to_symbol(self, level, duration):
        level_char = "H" if level else "L"
        duration_char = self.classify_duration(duration)

        return level_char + duration_char

    @staticmethod
    def classify_duration(duration):
        if 250 <= duration <= 500:
            return "S"

        if 600 <= duration <= 900:
            return "L"

        return "?"

    @staticmethod
    def bits_to_hex(bits):
        if "?" in bits:
            return None

        pad_len = (-len(bits)) % 4
        padded = bits + ("0" * pad_len)

        value = int(padded, 2)
        hex_len = len(padded) // 4

        return f"{value:0{hex_len}X}"

    def handle_frame(self, frame_hex, bits):
        frame_hex = frame_hex.upper()

        if not frame_hex.endswith(self.target_suffix):
            if self.debug:
                print(f"Ignored non-matching frame: {frame_hex}")
            return

        now = time.time()

        if now - self.last_trigger_time < self.cooldown_seconds:
            return

        self.last_trigger_time = now

        frame = RFFrame(
            frame_hex=frame_hex,
            bits=bits,
            timestamp=datetime.now(),
        )

        if self.on_press is not None:
            self.on_press(frame)
        else:
            print("BUTTON PRESSED")
            print(f"Time:  {frame.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Frame: {frame.frame_hex}")
            print()