#!/usr/bin/env python3
"""
Generate PEP 503 compliant simple repository index for GitHub Pages.
This script fetches all releases and creates the necessary index.html files.
"""

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
import html


def normalize_package_name(name):
    """Normalize package name according to PEP 503."""
    return name.lower().replace("_", "-").replace(".", "-")


def get_releases():
    """Fetch the newest release using gh CLI."""
    try:
        # First, get the list of release tags
        result = subprocess.run(
            ["gh", "release", "list", "--json", "tagName,publishedAt", "--limit", "100"],
            capture_output=True,
            text=True,
            check=True
        )
        releases = json.loads(result.stdout)
        # Only index the newest release. The previous one is kept for a day so the
        # currently deployed index never links to deleted wheels, but it isn't listed.
        releases = sorted(releases, key=lambda r: r["publishedAt"], reverse=True)[:1]

        # Then fetch assets for each release
        for release in releases:
            tag = release["tagName"]
            result = subprocess.run(
                ["gh", "release", "view", tag, "--json", "assets"],
                capture_output=True,
                text=True,
                check=True
            )
            release_data = json.loads(result.stdout)
            release["assets"] = release_data.get("assets", [])

        return releases
    except subprocess.CalledProcessError as e:
        print(f"Error fetching releases: {e}")
        print(f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: gh CLI not found. Please install GitHub CLI.")
        sys.exit(1)


def create_package_index(output_dir, repo_url, releases):
    """Create the package-specific index.html file."""
    package_dir = output_dir / "bpy"
    package_dir.mkdir(parents=True, exist_ok=True)

    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "  <meta charset='utf-8'>",
        "  <title>Links for bpy</title>",
        "</head>",
        "<body>",
        "  <h1>Links for bpy</h1>",
    ]

    # Collect all wheel files from all releases
    wheels = []
    for release in releases:
        tag = release["tagName"]
        for asset in release.get("assets", []):
            if asset["name"].endswith(".whl"):
                wheel_name = asset["name"]
                wheel_url = f"{repo_url}/releases/download/{tag}/{quote(wheel_name)}"
                wheels.append((wheel_name, wheel_url))

    # Sort wheels by name (newest first due to version in name)
    wheels.sort(reverse=True)

    # Add links to HTML
    for wheel_name, wheel_url in wheels:
        # Escape the wheel name for HTML
        escaped_name = html.escape(wheel_name)
        html_content.append(f"  <a href='{wheel_url}'>{escaped_name}</a><br/>")

    html_content.extend([
        "</body>",
        "</html>",
    ])

    index_file = package_dir / "index.html"
    index_file.write_text("\n".join(html_content))
    print(f"Created {index_file}")
    return len(wheels)


def create_root_index(output_dir):
    """Create the root index.html file listing all packages."""
    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "  <meta charset='utf-8'>",
        "  <title>Simple Index</title>",
        "</head>",
        "<body>",
        "  <h1>Simple Index</h1>",
        "  <a href='bpy/'>bpy</a><br/>",
        "</body>",
        "</html>",
    ]

    index_file = output_dir / "index.html"
    index_file.write_text("\n".join(html_content))
    print(f"Created {index_file}")


def create_readme(output_dir):
    """Create a README for the simple directory."""
    readme_content = """# PEP 503 Simple Repository Index

This directory contains a PEP 503 compliant simple repository index for custom bpy builds.

## Usage

Install bpy using this index:

```bash
# With uv
uv pip install bpy --extra-index-url https://bradyajohnston.github.io/dailybpy/

# With pip
pip install bpy --extra-index-url https://bradyajohnston.github.io/dailybpy/
```

## Configuration

Add to your `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "dailybpy"
url = "https://bradyajohnston.github.io/dailybpy/"
```

Then simply:

```bash
uv pip install bpy
```

This index is automatically generated from GitHub Releases.
"""

    readme_file = output_dir / "README.md"
    readme_file.write_text(readme_content)
    print(f"Created {readme_file}")


def main():
    """Main entry point."""
    # Get repository URL
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "url"],
            capture_output=True,
            text=True,
            check=True
        )
        repo_data = json.loads(result.stdout)
        repo_url = repo_data["url"]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting repository URL: {e}")
        print("Using default URL")
        repo_url = "https://github.com/BradyAJohnston/dailybpy"

    print(f"Repository URL: {repo_url}")

    # Create output directory
    output_dir = Path("simple")
    output_dir.mkdir(exist_ok=True)

    # Fetch releases
    print("Fetching releases...")
    releases = get_releases()
    print(f"Found {len(releases)} releases")

    # Generate index files
    print("Generating index files...")
    wheel_count = create_package_index(output_dir, repo_url, releases)
    create_root_index(output_dir)
    create_readme(output_dir)

    print(f"\nSuccess! Generated index with {wheel_count} wheel files.")
    print(f"Index location: {output_dir.absolute()}")
    print("\nTo test locally, run:")
    print(f"  cd simple && python -m http.server 8000")
    print(f"  pip install bpy --extra-index-url http://localhost:8000/")


if __name__ == "__main__":
    main()
