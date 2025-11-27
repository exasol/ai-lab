# Dependencies

## Multiple Types of Dependencies

AI Lab contains dependencies on multiple levels and specified in multiple places, each requiring specific steps for [updating dependencies](#updating-dependencies).

* [pyproject.toml](https://github.com/exasol/ai-lab/blob/main/pyproject.toml) and [poetry.lock](https://github.com/exasol/ai-lab/blob/main/poetry.lock)
* Requirements files in ansible scripts
  * [jupyter_requirements.txt](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/jupyter_requirements.txt)
  * [notebook_requirements.txt](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook_requirements.txt)
  * Including the notebook-connector and its dependencies
* Dependencies in other ansible scripts, e.g.
  * [docker/defaults/main.yml](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/docker/defaults/main.yml)
  * [roles/jupyter/defaults/main.yml](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/runtime/ansible/roles/jupyter/defaults/main.yml)
* AMI base image, see [lib/config.py](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/lib/config.py)
* Dependencies of the notebook tests in [test_dependencies.txt](https://github.com/exasol/ai-lab/blob/main/test/notebooks/test_dependencies.txt)
* GitHub Workflows and Actions:
  * no actual dependencies but references to actions of the Exasol Python Toolbox (PTB)
* [lib/dss_docker/Dockerfile](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/lib/dss_docker/Dockerfile)

### Ansible packages

The packages to be installed by Ansible are using pinned versions, e.g. for [docker](../../exasol/ds/sandbox/runtime/ansible/roles/docker/defaults/main.yml).

In case ansible reports "no available installation candidate" for a specific version of a package, please search for newer versions of the package on https://packages.ubuntu.com/ or https://www.ubuntuupdates.org/.

On `ubuntuupdates.org` you can use the [Package Search](https://www.ubuntuupdates.org/package_metas), please only use button "Package Search" or a URL like https://www.ubuntuupdates.org/package_metas?exact_match=1&q=network-manager.

If the update is very new and not yet displayed on packages.ubuntu.com you can use

```shell
sudo apt-get update
sudo apt search <package name>
sudo apt-get install <package name>=<version>
```

Maybe installing the command [chdist](https://manpages.ubuntu.com/manpages/questing/en/man1/chdist.1.html) could also be helpful, as it allows searching for packages and updates in other versions and distributions of ubuntu than the one installed on your local system.

### Find Packages in All Ansible Scripts

Shell function to find all packages in the ansible scripts

```shell
function ai-lab-ansible-dependencies() {
    local DIR=exasol/ds/sandbox/runtime/ansible/roles
    for i in $( find "$DIR" -name "*.yml"); do
        local DEPS=$(grep -E "[a-z]+=[0-9]" "$i")
        if [ -n "$DEPS" ]; then
            local LABEL=$(echo $i | sed -e "s|$DIR/||")
            echo -e "\n$LABEL:\n$DEPS"
        fi
    done
}
```
