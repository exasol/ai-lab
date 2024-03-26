# AI-Lab 1.1.0 released tbd

Code name: TBD

## Summary

tbd

This release changes the mount-point for Jupyter notebook files and the [Secure Configuration Storage](../user_guide/docker/secure-configuration-storage.md) from `/root/notebooks` to `/home/jupyter/notebooks`.
So in case you are mounting a volume containing your private notebook files into the AI-Lab's Docker container, then please change your scripts to use the new mounting point as described in the [User Guide](../user_guide/docker/docker-usage.md#creating-a-docker-container-for-the-ai--lab-from-the-ai-lab-docker-image).

Please note that the libraries and dependencies of the AI-Lab have changed since release 1.0.0 which can break some of the cells in old notebooks. So in case of problems, please do **not mount** notebook files created by an older version of the AI-Lab but create a new empty volume.

See also [Managing User Data](../user_guide/docker/managing-user-data.md).

## AI-Lab-Release

Version: 1.1.0

## Features

* #223: Added support to add docker image tag "latest"
* #204: Updated developer guide
* #177: Disabled core dumps
* #255: Changed owner of notebooks to jupyter in `entrypoint.py`

## Security

n/a

## Bug Fixes

* #241: Fixed non-root-user access

## Documentation

* #204: Updated developer guide
* #219: Described Virtual Box setup in user guide

## Refactoring

* #217: Changed notebook-connector dependency, now installing it from PyPi.
* #220: Changed default ports in the external database configuration.
* #221: Changed wording in the main configuration notebook, as suggested by PM.
* #66: Used a non-root user to run Jupyter in the Docker Image ai-lab
* #149: Split AWS tests
* #252: Added tests for access to Docker socket
