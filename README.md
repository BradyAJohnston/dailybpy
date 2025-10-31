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
- **Source**: [Blender official repository](https://github.com/blender/blender)

### Supported Platforms

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x86_64 | ✅ |
| macOS | ARM64 (Apple Silicon) | ✅ |
| Windows | x64 | ✅ |


## License

This repository contains build automation only. Blender is licensed under GPL v3. See the [Blender license](https://www.blender.org/about/license/) for details.
