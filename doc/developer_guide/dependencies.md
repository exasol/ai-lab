### Update dependencies

AI-Lab contains dependencies on multiple levels and specified in multiple places.

* [pyproject.toml](https://github.com/exasol/ai-lab/blob/main/pyproject.toml) impacting [poetry.lock](https://github.com/exasol/ai-lab/blob/main/poetry.lock)
* Requirements files in ansible scripts
  * [jupyter_requirements.txt](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/jupyter_requirements.txt)
  * [notebook_requirements.txt](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook_requirements.txt)
  * Including the notebook-connector and its dependencies SLCT and [slct_manager.py](https://github.com/exasol/notebook-connector/blob/main/exasol/nb_connector/slct_manager.py)
* Dependencies in other ansible scripts, e.g.
  * [docker/defaults/main.yml](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/docker/defaults/main.yml)
* AMI base image, see [exasol/ds/sandbox/lib/config.py](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/lib/config.py)
* GitHub Workflows: no actual dependencies

Commands to update operating system packages

```shell
sudo apt-get update
sudo apt-get install <package name>=<version>
sudo apt serarch <package name>
```