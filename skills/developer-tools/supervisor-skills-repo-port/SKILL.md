---
name: supervisor-skills-repo-port
description: Ports a skill that currently lives in the global skills directory into the Supervisor-Skills repository and registers it, or updates a skill already in that repository. Applies the repository's enforced conventions (English-only SKILL.md, 40-80 word description with a "Use when" clause, no em-dash, resolvable references pointers, references-only subdirectories, table of contents for long reference files), updates all seven registration points, runs the CI linter, and syncs the result back to the global skills directory. Use when the user says to save a skill into the Supervisor-Skills repository, to port or migrate a skill into that repo, to add a skill to that repo's skill set, or to optimise a skill that already lives there.
description_zh: 技能移植进 Supervisor-Skills 仓库
description_en: Port a skill into Supervisor-Skills
disable: false
agent_created: true
---

# Supervisor-Skills repo port

## When to use

- "把 skill 保存到本目录下进行更新" while the working directory is a
  Supervisor-Skills checkout.
- "把这个技能移植进仓库" / "在仓库里新增一个技能" / "把仓库里的这个
  技能优化一下".
- A skill exists at `~/.workbuddy/skills/<name>/` and the user wants
  the repository to become its source of truth.

## Repo contract (verify before writing anything)

Confirm these against the checkout every time; do not assume they are
unchanged.

1. `scripts/lint_skills.py` is the enforced linter, wired into
   `.github/workflows/lint.yml`. Read it before authoring.
2. Hard rules it enforces: `SKILL.md` body at most 500 lines; English
   only (no CJK in the SKILL.md body); `description` between 40 and 80
   words, third person, containing a "Use when" clause; no em-dash
   (U+2014) in `SKILL.md` or `references/*.md`; every
   `See: references/X.md` pointer and every `[...](references/X.md)`
   link resolves; reference files may not point at other reference
   files; reference files over 100 lines need a table of contents in
   the first 20 lines; no Claude or Anthropic attribution strings.
3. Directory shape is `SKILL.md` plus `references/*.md`, optionally
   `scripts/` and `assets/`. Do **not** invent `templates/`: the
   linter only scans `references/`, and pointers are only recognised
   with a `references/` prefix. Fold any `templates/` content into
   `references/`.
4. `scripts/check_shared_sync.py` enforces byte parity for reference
   files listed in its `SHARED` map. Adding a new shared file means
   editing that map too.
5. The linter needs PyYAML. If `python3 scripts/lint_skills.py` fails
   with "PyYAML is required", use
   `/Users/chenyliao/.workbuddy/binaries/python/envs/default/bin/python`
   (venv already carrying pyyaml) or `python -m pip install -r
   requirements-lint.txt` inside a venv.

## Steps

1. **Inventory both sides.** List the source skill directory and the
   target repo checkout. Read the source `SKILL.md` and every file
   under its `references/`, `templates/`, `scripts/`. Read one or two
   existing repo skills (for example `skills/tech-paper-template/`)
   to copy the house style: `## Overview`, `## When to use this
   skill`, `## When NOT to use this skill`, a `## Integrity gate`
   section, and a `## References` list of markdown links.
2. **Fix the parameters with the user** if the target name, the
   subdirectory layout, or the language of the reference files is
   ambiguous. Default to English throughout, matching every other
   skill in the repo.
3. **Write `skills/<name>/SKILL.md`.** Rewrite, do not transliterate:
   keep every domain-specific lesson, drop the scaffolding. Ground the
   content in the source's real measurements and named pitfalls.
4. **Move reference content into `references/`.** Rename to
   descriptive house-style filenames. Add a `## Contents` block when a
   file exceeds 100 lines. Never write a `See: references/...` line
   inside a reference file.
5. **Constrain cross-skill references to skills that exist in the
   repository.** Naming a global-only skill produces a dangling
   reference; phrase those as "if a dedicated X skill is installed in
   the environment" instead.
6. **Update all seven registration points**, each with one edit call:
   `README.md`, `README.en.md`, `skills/README.md`,
   `skills/README.en.md`, `llms.txt`, `CONTRIBUTING.md`,
   `CHANGELOG.md`. Bump the described skill count (eleven to twelve,
   and so on) everywhere it appears, add the file-tree entry, the
   skills-table row, a reader-guide card, a trigger-phrase line, and a
   handbook-mapping row. The skill-list sentence in `CONTRIBUTING.md`
   and the count in `llms.txt` are easy to miss.
7. **Run the gate.**
   ```bash
   cd <repo>
   <venv-python> scripts/lint_skills.py
   <venv-python> scripts/check_shared_sync.py
   ```
   Both must exit 0. Fix and rerun until clean.
8. **Sync back to the global skills directory** when the user wants
   the improvement live. Move the existing global directory aside to
   `~/.workbuddy/skill-backups/<name>-<lang>-<date>/` (move, never
   delete), copy the new `SKILL.md` and `references/`, then re-inject
   the runtime-only frontmatter fields the repo file does not carry:
   `description_zh`, `description_en`, `disable: false`,
   `agent_created: true`.
9. **Refresh any packaged archive.** If the checkout contains a
   `skills.zip`, rebuild it with
   `zip -r -X -FS skills.zip skills -x '*.DS_Store' -x '__MACOSX/*'`
   and confirm the new skill appears and the `__MACOSX` entries are
   gone.
10. **Report, then stop.** Give the file list, the lint result, and
    the diff summary. Do not commit or push without an explicit
    request.

## Pitfalls

- **Two edits to the same file in one message can silently lose the
  first one.** Observed three times in a single session: the tool
  reports success for both, but only one write lands. Edit one file
  per message, and re-grep after every batch to confirm.
- **`grep` with `\|` alternation fails silently under BSD grep on
  macOS**, returning an empty result that looks like a pass. Use the
  Grep tool, or run separate literal patterns.
- **The source `description` cannot be reused.** A Chinese
  description fails the word-count and CJK rules at once. Write a new
  English one and count the words before writing the file.
- **Em-dashes hide in prose.** The linter only rejects U+2014; write
  commas, colons or parentheses instead. En-dashes and arrows pass
  but read worse in English.
- **Stage IDs are load-bearing.** When porting a skill whose stages
  are referenced by the user's existing maintenance logs, keep the
  IDs stable and add an ordering column instead of renumbering.
- **Renaming a reference file breaks every pointer.** Grep the whole
  skill directory for the old name after any rename.
- **Do not touch unrelated skills in the same edit.** The linter
  report is per repository, so a stray edit elsewhere surfaces as a
  confusing failure.

## Verification

- [ ] `scripts/lint_skills.py` exits 0 and reports the expected skill
      count.
- [ ] `scripts/check_shared_sync.py` exits 0.
- [ ] No CJK and no U+2014 anywhere in the new `SKILL.md` or its
      `references/*.md`.
- [ ] Every `references/` target named in `SKILL.md` exists.
- [ ] All seven registration points mention the new skill; no stale
      skill-count wordings remain (grep for the old number and its
      English spelling).
- [ ] Global skills directory holds the updated copy, and the previous
      version is preserved under `~/.workbuddy/skill-backups/`.
- [ ] Any `skills.zip` in the checkout contains the new skill.
