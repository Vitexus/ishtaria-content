# ishtaria-content

<img src="https://git.vitexsoftware.com/Ishtaria/ishtaria-client/raw/branch/main/assets/branding/emblem.png" alt="Ishtaria" width="96">

<!-- source-notice -->
> **Primary source:** <https://git.vitexsoftware.com/Ishtaria/ishtaria-content> (development happens there). **GitHub** (<https://github.com/Vitexus/ishtaria-content>) is a secondary mirror; packages and binaries are **not built from GitHub**.
<!-- /source-notice -->

Base content pack `core-rules`: item kinds, recipes, species and biomes shared by every Ishtaria world. Worlds federate only when they share the major version of this ruleset.

```
core-rules/
  ruleset.yaml   items/   recipes/   species/   biomes/
```

Installed by `ishtaria-content` to `/usr/share/ishtaria/content/`.

License: CC BY-SA 4.0

## Part of Ishtaria

Ishtaria is an open-source, persistent, federated virtual planet of Earth size.
Documentation: https://vitexsoftware.github.io/ishtaria-docs/ · All repositories: https://git.vitexsoftware.com/Ishtaria

## Animation policy

Character and animation files live in `animations/<category>/<name>.glb` and `characters/<name>/<name>.glb`, with Blender
sources under `src/` where the licence allows. Everything is glTF 2.0 (`.glb`).

* **Shared rig.** Every avatar and animation uses the Quaternius Universal Animation Library (UAL) skeleton, so animations
  stay shareable between characters. Custom animations are made in Blender with Rigify and retargeted to that skeleton.
* **Licences.** Only CC0-1.0, CC-BY-4.0 and CC-BY-SA-4.0 are accepted, and each file must have an entry in `ASSETS.yaml`
  with its source URL, author, licence, retrieval date and whether it was modified.
* **Mixamo is forbidden.** Its licence does not allow redistributing character or animation files, which is what this repository
  does. This includes anything retargeted from Mixamo motions. The checker rejects the `mixamorig` bone prefix, the string
  `mixamo` in file names, file contents or manifest entries, and compressed `.blend` files it cannot inspect.
* **Checks.** `python3 tools/check_assets.py` runs in CI (Forgejo Actions, `.forgejo/workflows/assets.yml`) and in `debian/rules`. It also verifies
  that `debian/copyright` is generated from `ASSETS.yaml` (`python3 tools/generate_copyright.py`). Tests:
  `python3 -m unittest discover -s tests -v`.
