#!/usr/bin/env python3
"""Writes the release files for a build of the Keyboard Curator fork of the
Defy wireless firmware: `manifest.json` and `SHA256SUMS` beside the firmware
files in a directory.

Usage: tools/manifest.py <dist dir> <version> [<keyscanner source note>]

The manifest names the commits the build was made from (this repository,
its libraries, and the Kaleidoscope fork), the Dygma release it is based
on, the toolchain, the Focus commands the fork adds, and each file with
its SHA-256 and, for the Neuron image, its address range. Keyboard Curator
checks all of it before offering the firmware.
"""

import hashlib
import json
import os
import pathlib
import subprocess
import sys

try:
    from intelhex import IntelHex
except ImportError:  # the build needs it anyway
    IntelHex = None

HERE = pathlib.Path(__file__).resolve().parent.parent
BASE = {"repository": "Dygmalab/NeuronWireless_defy", "tag": "N2_Defy_v2.2.1"}
FOCUS = ["chords.map", "chords.timeout", "chords.memory", "timing.map", "timing.capacity", "timing.defaults"]


def git(*args, cwd=HERE):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(dist, version, keyscanner_from):
    dist = pathlib.Path(dist)
    artifacts = []
    neuron = dist / "Wireless_neuron.hex"
    if neuron.exists():
        entry = {"kind": "neuron", "file": neuron.name, "sha256": sha256(neuron), "chip": "nRF52833"}
        if IntelHex is not None:
            image = IntelHex(str(neuron))
            entry["addressStart"] = hex(image.minaddr())
            entry["addressEnd"] = hex(image.maxaddr() + 1)
        artifacts.append(entry)
    keyscanner = dist / "keyscanner.bin"
    if keyscanner.exists():
        artifacts.append({"kind": "keyscanner", "file": keyscanner.name, "sha256": sha256(keyscanner), "from": keyscanner_from})
    manifest = {
        "schema": 1,
        "project": "defy-curator",
        "version": version,
        "source": {
            "repository": "mroboff/NeuronWireless_defy",
            "commit": git("rev-parse", "HEAD"),
            "dirty": git("status", "--porcelain", "--untracked-files=no") != "",
        },
        "libraries": {"repository": "mroboff/NeuronWirelessLibs", "commit": git("rev-parse", "HEAD", cwd=HERE / "libraries")},
        "kaleidoscope": {
            "repository": "mroboff/Kaleidoscope-Dygma",
            "commit": git("rev-parse", "HEAD", cwd=HERE / "libraries" / "Kaleidoscope"),
        },
        "base": dict(BASE, commit=git("rev-parse", BASE["tag"] + "^{commit}")),
        "toolchain": {"gcc": os.environ.get("CURATOR_GCC_VERSION", "arm-none-eabi-gcc 10.3.1"), "sdk": "nRF5_SDK_17.1.0_ddde560"},
        "focus": FOCUS,
        "artifacts": artifacts,
    }
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with (dist / "SHA256SUMS").open("w") as sums:
        for entry in artifacts:
            sums.write(f"{entry['sha256']}  {entry['file']}\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Dygmalab/Firmware-release Defy_v2.2.1")
