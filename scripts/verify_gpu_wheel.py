#!/usr/bin/env python3
"""Check that a built bpy wheel has NVIDIA (CUDA + OptiX) support in Cycles.

Runs on CI machines without a GPU, so it only checks what is fixed at build
time: the precompiled kernel files in the wheel, and the device types Cycles
was compiled with. It does not try to enumerate devices.

Usage:
    verify_gpu_wheel.py WHEEL --archs "sm_75;sm_86;sm_120;compute_75" [--python PY]

--python is the interpreter (with the wheel installed) used for the import
check. Without it, only the wheel contents are checked.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import zipfile

IMPORT_CHECK = r"""
import bpy, _cycles
print("bpy", bpy.app.version_string)
print("_cycles.get_device_types():", _cycles.get_device_types())
prefs = bpy.context.preferences.addons["cycles"].preferences
items = [item[0] for item in prefs.get_device_types(bpy.context)]
print("compute_device_type items:", items)
assert "CUDA" in items, items
assert "OPTIX" in items, items
# Assigning validates against the enum items.
prefs.compute_device_type = "OPTIX"
prefs.compute_device_type = "CUDA"
print("OK: CUDA and OPTIX compute device types are available")
"""


def check_kernels(wheel, archs):
    names = zipfile.ZipFile(wheel).namelist()
    kernels = sorted(
        n for n in names if re.search(r"/cycles/lib/kernel_[^/]*\.zst$", n)
    )
    print(f"Cycles kernel files in {os.path.basename(wheel)}:")
    for name in kernels:
        print("  " + name)
    present = {os.path.basename(n) for n in kernels}
    required = [
        f"kernel_{a}.ptx.zst" if a.startswith("compute_") else f"kernel_{a}.cubin.zst"
        for a in archs
    ]
    required += ["kernel_optix.ptx.zst", "kernel_optix_shader_raytrace.ptx.zst"]
    missing = [r for r in required if r not in present]
    if missing:
        sys.exit(f"FAIL: missing kernel files in wheel: {missing}")
    print("OK: all required CUDA and OptiX kernel files are present")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel")
    parser.add_argument("--archs", required=True, help="';'-separated CUDA archs")
    parser.add_argument("--python", help="interpreter that has the wheel installed")
    args = parser.parse_args()

    check_kernels(args.wheel, [a for a in args.archs.split(";") if a])

    if args.python:
        # Run from an empty directory so nothing local shadows the installed bpy.
        with tempfile.TemporaryDirectory() as cwd:
            subprocess.run([args.python, "-c", IMPORT_CHECK], cwd=cwd, check=True)


if __name__ == "__main__":
    main()
