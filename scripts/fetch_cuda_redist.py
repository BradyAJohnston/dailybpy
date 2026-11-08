#!/usr/bin/env python3
"""Install a minimal CUDA toolkit (nvcc + headers) from NVIDIA's redist archives.

Used on Windows runners, where the full installer is slow and large. Only the
components needed to compile Cycles kernels with nvcc are fetched.

Usage:
    fetch_cuda_redist.py VERSION PLATFORM DEST
    fetch_cuda_redist.py 13.4.3 windows-x86_64 C:/cuda
"""

import hashlib
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://developer.download.nvidia.com/compute/cuda/redist/"
COMPONENTS = [
    "cuda_nvcc",
    "cuda_cudart",
    "cuda_crt",
    "cccl",
    "libnvvm",
    "libnvptxcompiler",
    "cuda_profiler_api",
]


def main():
    version, platform, dest = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    with urllib.request.urlopen(f"{BASE}redistrib_{version}.json") as f:
        manifest = json.load(f)
    dest.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name in COMPONENTS:
            if name not in manifest or platform not in manifest[name]:
                print(f"Skipping {name}: not in {version} for {platform}")
                continue
            entry = manifest[name][platform]
            archive = tmp / Path(entry["relative_path"]).name
            print(f"Downloading {name} {manifest[name]['version']}")
            urllib.request.urlretrieve(BASE + entry["relative_path"], archive)
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            if digest != entry["sha256"]:
                sys.exit(f"sha256 mismatch for {archive.name}")

            extract_dir = tmp / name
            if archive.suffix == ".zip":
                zipfile.ZipFile(archive).extractall(extract_dir)
            else:
                with tarfile.open(archive) as tar:
                    tar.extractall(extract_dir)
            # Each archive has a single top-level "<name>-<platform>-<ver>-archive" dir.
            (top,) = list(extract_dir.iterdir())
            shutil.copytree(top, dest, dirs_exist_ok=True)
            shutil.rmtree(extract_dir)
            archive.unlink()

    nvcc = dest / "bin" / ("nvcc.exe" if platform.startswith("windows") else "nvcc")
    if not nvcc.exists():
        sys.exit(f"nvcc not found at {nvcc}")
    print(f"CUDA {version} installed to {dest}")


if __name__ == "__main__":
    main()
