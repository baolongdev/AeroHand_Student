"""Installation checks only: no COM port or hand movement."""
import ast
import importlib.metadata
import struct
import sys
from pathlib import Path
import tkinter
import serial
import esptool
import aero_open_sdk
from aero_open_sdk import gui

root = Path(__file__).resolve().parents[1]
expected = (root / "aero-hand-open/sdk/src/aero_open_sdk").resolve()
actual = Path(aero_open_sdk.__file__).resolve().parent
assert actual == expected, f"Wrong SDK: {actual}"
assert sys.version_info >= (3, 10) and struct.calcsize("P") == 8
tree = ast.parse(Path(gui.__file__).read_text(encoding="utf-8"))
gated = any(isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
            and n.value.value is False and any(isinstance(t, ast.Attribute)
            and t.attr == "position_stream_enabled" for t in n.targets) for n in ast.walk(tree))
assert gated, "GUI must start with position streaming OFF"
assert (actual / "assets/logo.png").is_file()
assert (root / "aero-hand-open/firmware/main/bin/firmware_v0.2.0_lefthand.bin").is_file()
print("Python:", sys.version.split()[0], "64-bit")
print("SDK:", actual)
print("pyserial:", serial.__version__, "esptool:", importlib.metadata.version("esptool"))
print("Tcl:", tkinter.Tcl().eval("info patchlevel"))
print("OK: local SDK, GUI starts paused, assets and left firmware found.")
print("No COM connection, no firmware flash, no motor commands.")
