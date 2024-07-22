### Ansible packages

The packages to be installed by Ansible are using pinned versions, e.g. for [docker](../../exasol/ds/sandbox/runtime/ansible/roles/docker/defaults/main.yml).

In case ansible reports "no available installation candidate" for a specific version of a package, please search for newer versions of the package on https://packages.ubuntu.com/ or https://www.ubuntuupdates.org/.

On `ubuntuupdates.org` you can use the [Package Search](https://www.ubuntuupdates.org/package_metas), please only use button "Package Search" or a URL like https://www.ubuntuupdates.org/package_metas?exact_match=1&q=network-manager.

If the update is very new and not yet displayed on packages.ubuntu.com you can use

```shell
apt-get update
apt-search <package>
```

Maybe installing the command [chdist](https://manpages.ubuntu.com/manpages/xenial/en/man1/chdist.1.html) could also be helpful, as it allows searching for packages and updates in other versions and distributions of ubuntu than the one installed on your local system.
