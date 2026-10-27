"""Read and validate ASSETS.yaml, the provenance manifest of animation and character files."""

import datetime
import pathlib
import re

import yaml

MANIFEST = "ASSETS.yaml"

# Licences a file may carry, with the title Debian uses in /usr/share/common-licenses.
ALLOWED_LICENSES = {
    "CC0-1.0": "CC0 1.0 Universal",
    "CC-BY-4.0": "Creative Commons Attribution 4.0 International",
    "CC-BY-SA-4.0": "Creative Commons Attribution-ShareAlike 4.0 International",
}

ASSET_ROOTS = ("animations/", "characters/", "src/")
REQUIRED_KEYS = ("path", "source", "url", "author", "license", "retrieved", "modified")
STRING_KEYS = ("path", "source", "url", "author", "license")
UNSAFE_PATH = re.compile(r"[\s*?\[\]]")


def load_manifest(root):
    """Return (entries, problems) for the manifest under the repository root."""
    try:
        data = yaml.safe_load((pathlib.Path(root) / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [], [f"{MANIFEST}: cannot be read: {error}"]
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        return [], [f"{MANIFEST}: expected a mapping with an 'assets' list"]
    return data["assets"], []


def _is_date(value):
    if isinstance(value, datetime.date):
        return True
    try:
        datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def validate_entries(entries):
    """Return a list of problems with the manifest entries; an empty list means valid."""
    problems = []
    seen_paths = set()
    for number, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            problems.append(f"{MANIFEST} entry {number}: must be a mapping")
            continue
        path = entry.get("path")
        label = f"{MANIFEST} entry {number} ({path})"
        missing = [key for key in REQUIRED_KEYS if key not in entry]
        if missing:
            problems.append(f"{label}: missing {', '.join(missing)}")
            continue

        for key in STRING_KEYS:
            if not isinstance(entry[key], str) or not entry[key].strip():
                problems.append(f"{label}: '{key}' must be a non-empty string")
        if not isinstance(entry["modified"], bool):
            problems.append(f"{label}: 'modified' must be true or false")
        if not _is_date(entry["retrieved"]):
            problems.append(f"{label}: 'retrieved' must be a date (YYYY-MM-DD)")

        if isinstance(entry["license"], str) and entry["license"] not in ALLOWED_LICENSES:
            allowed = ", ".join(sorted(ALLOWED_LICENSES))
            problems.append(f"{label}: licence {entry['license']!r} is not allowed; use one of {allowed}")
        if isinstance(entry["url"], str) and not entry["url"].startswith("https://"):
            problems.append(f"{label}: 'url' must be an https:// link to the original source")

        if isinstance(path, str):
            posix = pathlib.PurePosixPath(path)
            if (
                not path.startswith(ASSET_ROOTS)
                or posix.is_absolute()
                or ".." in posix.parts
                or UNSAFE_PATH.search(path)
            ):
                problems.append(
                    f"{label}: path must be relative, start with animations/, characters/ or src/, "
                    "and contain no spaces or glob characters"
                )
            if path in seen_paths:
                problems.append(f"{label}: path is listed more than once")
            seen_paths.add(path)

        for key, value in entry.items():
            if isinstance(value, str) and "mixamo" in value.lower():
                problems.append(f"{label}: '{key}' mentions Mixamo, which is never allowed")
            if isinstance(value, str) and "\n" in value:
                problems.append(f"{label}: '{key}' must be a single line")
    return problems
