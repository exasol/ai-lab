---
name: Create Release
about: Create a new release of the AI-Lab
title: "\U0001F4E6 Create Release <version>"
labels: task
assignees: ''

---

* [ ] Adjust version number in file `pyproject.toml`

If you decided to change the version number then
* [ ] Run `poetry run -- version-check <path/version.py> --fix` (only when using PTB)
* [ ] Rename latest file `doc/changes/changes_*.md` accordingly
* [ ] Update reference in file `doc/changes/changelog.md`
* [ ] Update version number in latest file `doc/changes/changes_*.md`

Always
* latest file `doc/changes/changes_*.md`
  * [ ] Append release date to first line
  * [ ] Add a code name and a summary
* Update version number
  * [ ] `user_guide/docker/docker-usage.md`
  * [ ] `user_guide/vm-edition/win-vbox.md`
  * [ ] `developer_guide/testing.md`
* Replace dependencies to unreleased version (e.g. git dependencies) in files, see instructions in [notebooks.md](https://github.com/exasol/ai-lab/blob/main/doc/developer_guide/notebooks.md):
  * [ ] [notebook_requirements.txt](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook_requirements.txt)
  * [ ] [jupyter_requirements.txt](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/jupyter_requirements.txt)
  * [ ] [pyproject.toml](https://github.com/exasol/ai-lab/blob/main/pyproject.toml)

Ship the Actual Release
* [ ] Run release droid `java -jar ~/java/jar/release-droid-*.jar -n ai-lab --goal release`
* [ ] Edit the Release on GitHub making the draft final

Post-Release Actions
* [ ] Update links in file `README.md` to point to the tag on GitHub
