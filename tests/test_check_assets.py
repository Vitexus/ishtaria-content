"""Tests for tools/check_assets.py and tools/generate_copyright.py.

Run from the repository root: python3 -m unittest discover -s tests -v
"""

import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import asset_manifest  # noqa: E402
import check_assets  # noqa: E402
import generate_copyright  # noqa: E402

GOOD_ENTRY = """\
assets:
  - path: animations/locomotion/walk.glb
    source: Quaternius Universal Animation Library 1
    url: https://quaternius.com/
    author: Quaternius
    license: CC0-1.0
    retrieved: 2026-10-01
    modified: false
"""


class RepoTestCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        (self.root / "debian").mkdir()

    def write(self, relative, content=b""):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode() if isinstance(content, str) else content)

    def sync_copyright(self):
        entries, _ = asset_manifest.load_manifest(self.root)
        if asset_manifest.validate_entries(entries):
            return
        self.write("debian/copyright", generate_copyright.render(entries))

    def problems(self):
        return check_assets.check_repository(self.root)

    def assertProblem(self, fragment):
        matches = [problem for problem in self.problems() if fragment in problem]
        self.assertTrue(matches, f"no problem mentioning {fragment!r}: {self.problems()}")


class CheckAssetsTest(RepoTestCase):
    def test_empty_repository_passes(self):
        self.write("ASSETS.yaml", "assets: []\n")
        self.sync_copyright()
        self.assertEqual(self.problems(), [])

    def test_listed_asset_passes(self):
        self.write("ASSETS.yaml", GOOD_ENTRY)
        self.write("animations/locomotion/walk.glb", b"glTF\x02\x00\x00\x00")
        self.sync_copyright()
        self.assertEqual(self.problems(), [])

    def test_uncompressed_blend_source_passes(self):
        self.write(
            "ASSETS.yaml",
            GOOD_ENTRY.replace("animations/locomotion/walk.glb", "src/rig.blend"),
        )
        self.write("src/rig.blend", b"BLENDER-v500")
        self.sync_copyright()
        self.assertEqual(self.problems(), [])

    def test_unlisted_asset_fails(self):
        self.write("ASSETS.yaml", "assets: []\n")
        self.write("characters/hero/hero.glb", b"glTF")
        self.sync_copyright()
        self.assertProblem("characters/hero/hero.glb: no entry in ASSETS.yaml")

    def test_listed_but_missing_file_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY)
        self.sync_copyright()
        self.assertProblem("animations/locomotion/walk.glb: listed in ASSETS.yaml but missing")

    def test_disallowed_licence_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("CC0-1.0", "CC-BY-NC-4.0"))
        self.write("animations/locomotion/walk.glb", b"glTF")
        self.sync_copyright()
        self.assertProblem("licence 'CC-BY-NC-4.0' is not allowed")

    def test_mixamo_bone_prefix_in_content_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY)
        self.write("animations/locomotion/walk.glb", b'{"name": "mixamorig:Hips"}')
        self.sync_copyright()
        self.assertProblem("animations/locomotion/walk.glb: contains the Mixamo fingerprint")

    def test_mixamo_in_file_name_fails(self):
        self.write("animations/locomotion/mixamo_walk.glb", b"glTF")
        self.write("ASSETS.yaml", "assets: []\n")
        self.sync_copyright()
        self.assertProblem("file name mentions Mixamo")

    def test_mixamo_in_manifest_source_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("Quaternius Universal", "Mixamo Universal"))
        self.write("animations/locomotion/walk.glb", b"glTF")
        self.sync_copyright()
        self.assertProblem("'source' mentions Mixamo")

    def test_compressed_blend_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("animations/locomotion/walk.glb", "src/rig.blend"))
        self.write("src/rig.blend", b"\x28\xb5\x2f\xfd" + b"\x00" * 16)
        self.sync_copyright()
        self.assertProblem("compressed .blend cannot be inspected")

    def test_out_of_date_copyright_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY)
        self.write("animations/locomotion/walk.glb", b"glTF")
        self.write("debian/copyright", "Format: outdated\n")
        self.assertProblem("debian/copyright is out of sync")

    def test_path_traversal_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("animations/locomotion/walk.glb", "animations/../../x.glb"))
        self.assertProblem("path must be relative")

    def test_path_outside_asset_roots_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("animations/locomotion/walk.glb", "docs/walk.glb"))
        self.assertProblem("path must be relative")

    def test_duplicate_path_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY + GOOD_ENTRY.split("assets:\n", 1)[1])
        self.write("animations/locomotion/walk.glb", b"glTF")
        self.assertProblem("listed more than once")

    def test_non_date_retrieved_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("2026-10-01", "last week"))
        self.assertProblem("'retrieved' must be a date")

    def test_impossible_retrieved_date_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("2026-10-01", "2026-13-01"))
        self.assertProblem("ASSETS.yaml: cannot be read")

    def test_non_https_url_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("https://quaternius.com/", "http://quaternius.com/"))
        self.assertProblem("'url' must be an https://")

    def test_missing_key_fails(self):
        self.write("ASSETS.yaml", GOOD_ENTRY.replace("    author: Quaternius\n", ""))
        self.assertProblem("missing author")

    def test_unreadable_manifest_fails(self):
        self.write("ASSETS.yaml", "assets: [\n")
        self.assertProblem("ASSETS.yaml: cannot be read")

    def test_this_repository_passes(self):
        self.assertEqual(check_assets.check_repository(ROOT), [])


class GenerateCopyrightTest(RepoTestCase):
    def test_render_sorts_assets_and_adds_licence_stanzas(self):
        entries = [
            {
                "path": "characters/hero/hero.glb",
                "source": "Quaternius",
                "url": "https://quaternius.com/",
                "author": "Quaternius",
                "license": "CC-BY-4.0",
                "retrieved": "2026-10-02",
                "modified": True,
            },
            {
                "path": "animations/locomotion/walk.glb",
                "source": "Quaternius",
                "url": "https://quaternius.com/",
                "author": "Quaternius",
                "license": "CC0-1.0",
                "retrieved": "2026-10-01",
                "modified": False,
            },
        ]
        text = generate_copyright.render(entries)
        self.assertLess(text.index("Files: animations/"), text.index("Files: characters/"))
        self.assertIn("Comment: Source: https://quaternius.com/ (retrieved 2026-10-02, modified: yes)", text)
        self.assertIn('"/usr/share/common-licenses/CC0-1.0"', text)
        self.assertIn('"/usr/share/common-licenses/CC-BY-4.0"', text)
        self.assertIn('"/usr/share/common-licenses/CC-BY-SA-4.0"', text)
        self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
