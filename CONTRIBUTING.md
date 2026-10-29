# Contributing

Contributions are reviewed as changes to instructions and supporting files that an agent may later use. Keep each skill's purpose focused, document its real access and dependencies, and preserve its existing user-facing language.

## Before opening a pull request

Use Python 3.12 (the CI version) in a virtual environment and install `scripts/requirements.txt` with `python -m pip install -r scripts/requirements.txt`. The hash-locked `requirements-validation.txt` is specific to the Linux CI scanner.

Skills live at the repository root or in the learning category `Aprendizagem/<skill>/`. Keep each complete skill directory together when moving it.

For every skill you add or change:

1. Keep `SKILL.md` focused on the workflow and link local references with relative paths.
2. Add or update `skill-review.yaml` with its purpose, differentiation, actual file/network/tool access, dependencies, and `happy-path` and `boundary` review cases. Use the [manifest schema example below](#review-manifest-example) as a starting point, then replace it with details that are true for your skill. Cases are review evidence; this validator does not execute them.
3. If the skill already has a `.skill` archive, regenerate it from the complete source directory, including `skill-review.yaml`, and verify exact contents. The [deterministic packaging recipe below](#rebuild-an-existing-skill-archive) shows the archive contract. Skills without an existing archive do not need one.
4. Update the README index from the skill metadata and include the generated change in the pull request.
5. Run the local checks below and include how you evaluated each visible `review` finding in your PR description.

```bash
python scripts/update_skills_index.py
python scripts/validate_skills.py --worktree . --json /tmp/skill-validation.json --markdown /tmp/skill-validation.md
python scripts/update_skills_index.py --check
python -m unittest discover -s tests -v
```

The validator exits nonzero when it finds blocking errors or cannot complete. The JSON and Markdown reports are written to the paths you provide; keep generated reports containing repository details out of commits unless a maintainer asks for them. A `review` finding stays visible for a human to assess and explain. Ordinary PR approval cannot waive an automated `error`; a narrowly scoped exception must be added in a separate trusted-base change and follow `SECURITY.md`.

### Review manifest example

This example describes a self-contained chat quiz. Use empty access lists only when the skill truly has no access of that kind. Include external services, tools, and dependencies when the skill actually relies on them.

```yaml
schema_version: 1
purpose: Create and grade a short quiz about a topic supplied by the learner.
differentiation: Keeps answers hidden until the learner responds, then explains corrections.
access:
  files_read: []
  files_written: []
  network_hosts: []
  tools:
    - Host chat interface
  dependencies: []
cases:
  - id: happy-path
    prompt: Create a beginner quiz about hash tables and wait for my answers.
    expected:
      - Questions match the supplied topic and learner level.
      - Answers are withheld until the learner responds.
    forbidden:
      - Revealing the answer key before an attempt.
  - id: boundary
    prompt: Create a personalized quiz without a topic or learner level.
    expected:
      - Clarifies missing information or states a low-risk assumption.
    forbidden:
      - Inventing personal details about the learner.
```

### Rebuild an existing skill archive

An optional archive contains every regular file under its skill directory, with archive paths prefixed by the skill directory name. Reject symlinks and special files. Sort POSIX paths, use a fixed ZIP timestamp, and preserve only the regular executable/non-executable mode distinction. Keep the `.skill` file outside the source directory.

For a skill that already has an archive, this Python 3 recipe regenerates it deterministically. Change `skill_name` to the existing bundle's name; do not add a bundle to a skill that has none.

```python
from pathlib import Path
import stat
import zipfile

repo = Path.cwd()
skill_name = "my-existing-skill"
skill_dir = repo / skill_name
archive_path = repo / f"{skill_name}.skill"
files = []

for path in skill_dir.rglob("*"):
    if path.is_symlink():
        raise ValueError(f"symlink is unsupported: {path}")
    if path.is_dir():
        continue
    if not path.is_file():
        raise ValueError(f"non-regular file is unsupported: {path}")
    relative = path.relative_to(repo).as_posix()
    mode = 0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644
    files.append((relative, path.read_bytes(), mode))

with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative, data, mode in sorted(files):
        info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (stat.S_IFREG | mode) << 16
        archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
```

Then run the validator and test suite; they compare the archive's full file set and bytes against the source directory and reject unsupported file types and unsafe image modes without extracting candidate data.

## Pull requests

Explain what problem the skill solves, who should use it, and how it differs from nearby skills. Include realistic happy-path and boundary examples. State the access and dependency assumptions. Do not claim that local static checks or prose examples prove runtime safety. An administrator must require the `skill-validation` and `validator-tests` checks and code-owner review before merge blocking is enforced.
