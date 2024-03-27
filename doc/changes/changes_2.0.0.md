# AI-Lab 2.0.0 released 2024-03-28

Code name: Use non-privileged user for running JupyterLab

## Summary

The following changes are especially important if you are using the AI-Lab's Docker Edition and are [mounting a volume](../user_guide/docker/managing-user-data.md) containing your private notebook files and the  [Secure Configuration Storage](../user_guide/docker/secure-configuration-storage.md)  (SCS) into the AI-Lab's Docker container.

Major changes

1. The mount-point for Jupyter notebook files and the SCS has moved from `/root/notebooks` to `/home/jupyter/notebooks`.
2. Some of the notebooks have been updated, especially the Cloud Storage Extension notebook.

In case you are using the AI-Lab's Docker Edition with mounted volume, then please
1. Change your commands to use the new mount point as described in the [User Guide](../user_guide/docker/docker-usage.md#creating-a-docker-container-for-the-ai--lab-from-the-ai-lab-docker-image) and
2. Find the updated notebooks in folder `/home/jupyter/notebook-defaults` as the AI-Lab does not overwrite existing files, to avoid losing manual changes.

## AI-Lab-Release

Version: 2.0.0

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
