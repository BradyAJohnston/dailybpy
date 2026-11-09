# Daily bpy Builds

[![Building bpy](https://github.com/BradyAJohnston/dailybpy/actions/workflows/build-bpy-module.yml/badge.svg)](https://github.com/BradyAJohnston/dailybpy/actions/workflows/build-bpy-module.yml)
[![Publish Package Index](https://github.com/BradyAJohnston/dailybpy/actions/workflows/publish-index.yml/badge.svg)](https://github.com/BradyAJohnston/dailybpy/actions/workflows/publish-index.yml)

Automated daily builds of Blender as a Python module (bpy) for Linux, macOS (ARM64), and Windows. These builds are run daily from the `main` branch of the [Blender](https://github.com/Blender/blender) repo which is an official mirror of the [Gitea](https://projects.blender.org/Blender/blender) development.

A repo for these builds is hosted at `bradyajohnston.github.io/dailybpy` so you can install using `uv` or `pip` from a custom repo to get the latest daily build as below.

## Installation

### `uv`
#### Install the Latest Alpha Build
```bash
uv pip install bpy --index https://bradyajohnston.github.io/dailybpy/
```

#### Install a specific version for beta / alpha
```bash
uv pip install "bpy==5.0.*" --index https://bradyajohnston.github.io/dailybpy/
```

Once the package becomes available through `pypi` it will fallback to installing from there instead.


### `pip`
```bash
pip install bpy --index-url https://bradyajohnston.github.io/dailybpy/
```

### Project Configuration

 Optionally configure your project to source `bpy` from these builds instead of pypi in the `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "bpy"
url = "https://bradyajohnston.github.io/dailybpy/"

[project]
dependencies = [
    "bpy",
]
```

Then install with:

```bash
uv pip install bpy
# or
uv sync
```

## About

- **Version**: built from the lasted main (alpha) branch
- **Build Schedule**: Daily at 2 AM UTC
- **Retention**: builds from the last 30 days stay available, e.g. `bpy==5.4.0a0+202611081101`
- **Source**: [Blender official repository](https://github.com/blender/blender)

### Supported Platforms

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x86_64 | ✅ |
| macOS | ARM64 (Apple Silicon) | ✅ |
| Windows | x64 | ✅ |

### GPU Support (Cycles)

| Backend | Linux | Windows | macOS |
|---------|-------|---------|-------|
| NVIDIA CUDA | ✅ | ✅ | — |
| NVIDIA OptiX | ✅ | ✅ | — |
| Apple Metal | — | — | ✅ |
| AMD HIP | ⚠️ | ⚠️ | — |
| Intel oneAPI | ❌ | ❌ | — |

- CUDA kernels are precompiled for Turing (`sm_75`), Ampere/Ada (`sm_86`) and Blackwell (`sm_120`), so GTX 16xx / RTX 20xx and newer cards work. Other NVIDIA GPUs fall back to JIT-compiling the `compute_75` PTX on first render.
- The builds use CUDA 13 and OptiX 9.0, so they need a recent NVIDIA driver (R580 or newer).
- AMD HIP support is compiled in, but no HIP kernels are precompiled. Without the HIP SDK installed to compile them at runtime (untested), AMD GPUs aren't usable.
- Intel oneAPI is not built. The official [PyPI builds](https://pypi.org/project/bpy/) include precompiled HIP and oneAPI kernels.


## License

This repository contains build automation only. Blender is licensed under GPL v3. See the [Blender license](https://www.blender.org/about/license/) for details.
