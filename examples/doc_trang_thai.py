"""Read-only telemetry. Close GUI first. Never sends movement/Homing commands."""
import argparse
import struct
import time
import serial

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--port", default="COM11")
args = parser.parse_args()
port = serial.Serial()
port.port, port.baudrate = args.port, 921600
port.timeout, port.write_timeout = 0.05, 1
port.dtr = False
port.rts = False

def query(op):
    port.reset_input_buffer()
    port.write(bytes([op]) + bytes(15))
    port.flush()
    deadline, data = time.monotonic() + 2, b""
    while time.monotonic() < deadline:
        data += port.read(64)
        start = data.find(bytes([op, 0]))
        if start >= 0 and len(data) >= start + 16:
            return data[start + 2:start + 16]
    raise TimeoutError("No reply: check port, firmware, 6 V and all seven IDs")

with port:
    print("IDs: 0, 1, 2, 3, 4, 5, 6")
    print("TEMP C:", struct.unpack("<7H", query(0x25)))
    print("CURRENT signed RAW counts (not mA):", struct.unpack("<7h", query(0x24)))
    print("POS normalized:", [round(x / 65535, 3) for x in struct.unpack("<7H", query(0x22))])
