#!/usr/bin/env python3
"""Check the built Windows extension publishes its declared Godot C entry only."""
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1] / "examples/summator"
commands = json.loads((root / "compile_commands.json").read_text(encoding="utf-8"))
entry = next(item for item in commands if Path(item["file"]).name == "summator.cpp")
reader = Path(entry["arguments"][0]).with_name("llvm-readobj.exe")
assert reader.is_file(), reader
binaries = list((root / "target").rglob("summator.dll"))
assert len(binaries) == 1, binaries
output = subprocess.check_output([str(reader), "--coff-exports", str(binaries[0])], text=True)
names = set(re.findall(r"^\s*Name:\s*(\S+)\s*$", output, re.M))
assert names == {"summator_library_init"}, output
print("Verified the sole Windows extension export: summator_library_init")
