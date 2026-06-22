#!/usr/bin/env python3
"""Append the build timestamp to a wheel's version as a PEP 440 local version segment.

Daily builds keep the same upstream version (e.g. ``5.1.0a0``) day after day, so
``pip``/``uv`` see an unchanged version and assume the installed wheel is already
up to date even though the build content changed. Rewriting the version to
``5.1.0a0+202606220200`` makes each build a distinct, strictly higher version,
so package managers pull and upgrade to the latest build.

Usage:
    python redate_wheels.py YYYYMMDDHHMM wheel1.whl [wheel2.whl ...]

The local version segment must be all digits (any monotonically increasing stamp
works). Each wheel is rewritten in place (the original file is replaced with the
re-versioned one) and the new path is printed.
"""

import base64
import hashlib
import re
import sys
import zipfile
from pathlib import Path


def _urlsafe_b64_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def redate_wheel(wheel_path: Path, stamp: str) -> Path:
    # wheel filename: {name}-{version}(-{build})?-{pytag}-{abitag}-{plattag}.whl
    # The name never contains '-' (runs of '-' are escaped to '_'), and a local
    # version segment never contains '-', so the version is always field index 1.
    parts = wheel_path.stem.split("-")
    name, version, tail = parts[0], parts[1], parts[2:]

    if "+" in version:
        raise SystemExit(f"{wheel_path.name}: version already has a local segment")

    new_version = f"{version}+{stamp}"
    old_distinfo = f"{name}-{version}.dist-info"
    new_distinfo = f"{name}-{new_version}.dist-info"
    out_path = wheel_path.with_name("-".join([name, new_version, *tail]) + ".whl")

    record_path = f"{new_distinfo}/RECORD"
    record_lines = []

    with zipfile.ZipFile(wheel_path) as zin, zipfile.ZipFile(
        out_path, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for info in zin.infolist():
            old_name = info.filename
            # The wheel's own RECORD is regenerated from scratch below.
            if old_name == f"{old_distinfo}/RECORD":
                continue

            blob = zin.read(old_name)
            new_name = old_name
            if old_name.startswith(old_distinfo + "/"):
                new_name = new_distinfo + old_name[len(old_distinfo):]

            if new_name == f"{new_distinfo}/METADATA":
                blob = re.sub(
                    rb"^Version: .*$",
                    f"Version: {new_version}".encode(),
                    blob,
                    count=1,
                    flags=re.MULTILINE,
                )

            # Preserve original ZipInfo (timestamps, permissions, compression).
            info.filename = new_name
            zout.writestr(info, blob)

            digest = _urlsafe_b64_nopad(hashlib.sha256(blob).digest())
            record_lines.append(f"{new_name},sha256={digest},{len(blob)}")

        record_lines.append(f"{record_path},,")
        zout.writestr(record_path, "\n".join(record_lines) + "\n")

    if out_path != wheel_path:
        wheel_path.unlink()
    return out_path


def main(argv):
    if len(argv) < 3 or not argv[1].isdigit():
        sys.exit("Usage: python redate_wheels.py YYYYMMDDHHMM wheel1.whl [wheel2.whl ...]")

    stamp, wheels = argv[1], argv[2:]
    for wheel in wheels:
        out = redate_wheel(Path(wheel), stamp)
        print(f"Re-versioned -> {out.name}")


if __name__ == "__main__":
    main(sys.argv)
