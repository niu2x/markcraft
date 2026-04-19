#!/usr/bin/env bash

set -euo pipefail

usage() {
    echo "Usage: $0 <new_version>"
    echo "   or: $0 <old_version> <new_version>"
}

if [[ $# -eq 1 ]]; then
    OLD_VERSION=""
    NEW_VERSION="$1"
elif [[ $# -eq 2 ]]; then
    OLD_VERSION="$1"
    NEW_VERSION="$2"
else
    usage
    exit 1
fi

if [[ ! $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "[Error] Version must match MAJOR.MINOR.PATCH (example: 1.2.3)."
    exit 1
fi

python - "$OLD_VERSION" "$NEW_VERSION" <<'PY'
from __future__ import annotations

import pathlib
import re
import sys


def replace_once(path: pathlib.Path, pattern: str, replacement: str) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"[Error] Expected exactly 1 match in {path}, got {count}.")
    path.write_text(updated, encoding="utf-8")
    return text, updated


old_from_arg = sys.argv[1]
new_version = sys.argv[2]

repo = pathlib.Path.cwd()
pyproject = repo / "pyproject.toml"
init_file = repo / "src/markcraft/__init__.py"
readme = repo / "README.md"

pyproject_text = pyproject.read_text(encoding="utf-8")
match = re.search(r'^version = "([^"]+)"$', pyproject_text, flags=re.MULTILINE)
if not match:
    raise SystemExit("[Error] Cannot find project version in pyproject.toml.")

current_version = match.group(1)
if old_from_arg and old_from_arg != current_version:
    raise SystemExit(
        "[Error] Provided old version does not match pyproject.toml: "
        f"{old_from_arg} != {current_version}"
    )

init_text = init_file.read_text(encoding="utf-8")
init_match = re.search(r'^__version__ = "([^"]+)"$', init_text, flags=re.MULTILINE)
if not init_match:
    raise SystemExit("[Error] Cannot find __version__ in src/markcraft/__init__.py.")

if init_match.group(1) != current_version:
    raise SystemExit(
        "[Error] Version mismatch between pyproject.toml and src/markcraft/__init__.py: "
        f"{current_version} != {init_match.group(1)}"
    )

if current_version == new_version:
    raise SystemExit(f"[Error] New version is the same as current version: {new_version}")

replace_once(pyproject, r'^version = "[^"]+"$', f'version = "{new_version}"')
replace_once(init_file, r'^__version__ = "[^"]+"$', f'__version__ = "{new_version}"')

readme_text = readme.read_text(encoding="utf-8")
updated_readme = readme_text.replace(f"v{current_version}", f"v{new_version}")
if readme_text != updated_readme:
    readme.write_text(updated_readme, encoding="utf-8")

print(f"[OK] Bumped version: {current_version} -> {new_version}")
print("[OK] Updated files: pyproject.toml, src/markcraft/__init__.py, README.md (if matched)")
PY

git diff -- pyproject.toml src/markcraft/__init__.py README.md
