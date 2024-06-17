# AI-Lab 2.1.0 released TBD

Code name: Exasol SaaS and Python 3.10

## Summary

This release adds support for parameters for SaaS instances of Exasol database to the configuration page and fixes vulnerability `CVE-2024-23342` by updating dependencies.

Additionally the release updates the operating system from ubuntu 20.04 to 22.04 and Python version to 3.10 in the published images for Docker, AMI, and virtual machines.

## AI-Lab-Release

Version: 2.1.0

## Features

* 277 Added the SaaS database parameters to the configuration page.
* 279 Made the notebooks tests running in SaaS as well as in the Docker-DB.

## Security

* #207 Fixed vulnerability CVE-2024-23342 by updating dependency ecdsa

## Bug Fixes

* #289 Fixed UI in notebooks

## Documentation

* #249: Added a troubleshooting section to the user guide documenting died kernel for transformers/te_init.ipynb.
* #284: Improved User Guide regarding Docker volumes

## Refactoring

* #267: Switched CodeBuildWaiter to use tenacity
* #276: Started using the new ITDE Manager interface in the notebook-connector 0.2.9
* #282: Updated python version to Python 3.10
