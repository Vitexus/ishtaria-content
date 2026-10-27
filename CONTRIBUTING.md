# Contributing to ishtaria-content

Thank you. ishtaria-content is the versioned base content pack `core-rules`: species, items, recipes, biomes, rulesets.

1. Read the [developer guide](https://git.vitexsoftware.com/Ishtaria/ishtaria-docs/src/branch/main/source/development): `invariants` (short, binding), `local-setup`, `cookbook`.
2. Open an issue for anything larger than a fix; architectural changes are written as a decision record first.
3. Make a small change with a test that fails without it (also for the refusal paths) and run the checks:

   ```sh
   python3 -c 'import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob("core-rules/**/*.y*ml", recursive=True)]'
   ```

4. Use Conventional Commits (`feat(ishtaria-content): ...`), branch from `main`, and fill in the pull request template:
   what you tested, what you could not test, what is still planned.

Working with Claude Code is welcome and expected: `CLAUDE.md` in this repository is read automatically. You are
responsible for the code you submit; read the diff, especially SQL, locking, validation and every place a client
value reaches a server.

By contributing you agree to license your work under CC-BY-SA-4.0 (see `LICENSE`).

## How to add an animation

1. Download the file from the original author's page (for example quaternius.com or its itch.io page), never from a re-upload
   site. Do not download files for an animation you do not yet need.
2. Check the licence is CC0-1.0, CC-BY-4.0 or CC-BY-SA-4.0. Anything else is rejected.
3. Make sure the file is rigged to the shared Universal Animation Library skeleton. Retargeting a character to it is the only
   accepted way to make another rig work. Do not add a second skeleton.
4. Put the file at `animations/<category>/<name>.glb`, or `characters/<name>/<name>.glb` for a character. Put a Blender
   source under `src/` only if its licence allows it.
5. Add an entry to `ASSETS.yaml` with `path`, `source`, `url`, `author`, `license`, `retrieved` (YYYY-MM-DD) and `modified`.
   Set `modified: true` after any retargeting or editing and describe the change in `source`.
6. Run the checks, then commit the regenerated `debian/copyright`:

   ```sh
   python3 tools/generate_copyright.py
   python3 tools/check_assets.py
   python3 -m unittest discover -s tests -v
   ```

**Why Mixamo is forbidden.** Mixamo's licence does not allow redistributing its character or animation files, and retargeting
its motions does not change that. Everything in this repository is redistributed under an open licence, so Mixamo files and
files derived from them are rejected. The checker enforces this from the `mixamorig` bone prefix and the word `mixamo` in file
names, contents and manifest entries.

**Auto-rigging helpers.** mesh2motion is an optional open-source rigging helper. Its bundled animations are not imported until
their licence has been verified and recorded in `ASSETS.yaml`.
