#!/usr/bin/env python3
"""Generate debian/copyright (DEP-5) from ASSETS.yaml.

    python3 tools/generate_copyright.py          write debian/copyright
    python3 tools/generate_copyright.py --check  exit 1 when it is out of date
"""

import pathlib
import sys

import asset_manifest

PROJECT_LICENCE = "CC-BY-SA-4.0"

HEADER = """\
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: ishtaria-content
Source: https://git.vitexsoftware.com/Ishtaria/ishtaria-content

Files: *
Copyright: 2026 Vítězslav Dvořák <cybervitexus@gmail.com>
License: CC-BY-SA-4.0
"""


def copyright_path(root):
    return pathlib.Path(root) / "debian" / "copyright"


def license_stanza(identifier):
    title = asset_manifest.ALLOWED_LICENSES[identifier]
    return (
        f"License: {identifier}\n"
        f" On Debian systems, the complete text of the {title} license can be found in\n"
        f' "/usr/share/common-licenses/{identifier}".\n'
    )


def asset_stanza(entry):
    modified = "yes" if entry["modified"] else "no"
    return (
        f"Files: {entry['path']}\n"
        f"Copyright: {entry['author']}\n"
        f"Comment: Source: {entry['url']} (retrieved {entry['retrieved']}, modified: {modified})\n"
        f"License: {entry['license']}\n"
    )


def render(entries):
    """Return the complete debian/copyright text for validated manifest entries."""
    stanzas = [HEADER]
    licences = {PROJECT_LICENCE}
    for entry in sorted(entries, key=lambda item: item["path"]):
        licences.add(entry["license"])
        stanzas.append(asset_stanza(entry))
    stanzas.extend(license_stanza(identifier) for identifier in sorted(licences))
    return "\n".join(stanzas)


def is_current(root, entries):
    try:
        return copyright_path(root).read_text(encoding="utf-8") == render(entries)
    except OSError:
        return False


def main(argv):
    root = pathlib.Path(__file__).resolve().parent.parent
    entries, problems = asset_manifest.load_manifest(root)
    problems += asset_manifest.validate_entries(entries)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    if "--check" in argv:
        if not is_current(root, entries):
            print("debian/copyright is out of date; run python3 tools/generate_copyright.py", file=sys.stderr)
            return 1
        return 0

    copyright_path(root).write_text(render(entries), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
