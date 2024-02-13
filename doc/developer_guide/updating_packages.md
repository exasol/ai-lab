### Ansible packages

The packages to be installed by Ansible are using pinned versions, e.g. for [docker](../../exasol/ds/sandbox/runtime/ansible/roles/docker/defaults/main.yml).

In case ansible reports "no available installation candidate" for a specific version of a package, please search for newer versions of the package on https://packages.ubuntu.com/.

If the update is very new and not yet displayed on packages.ubuntu.com you can use

```shell
apt-get update
apt-search <package>
```
