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
