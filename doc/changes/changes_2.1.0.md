# AI-Lab 2.1.0 released TBD

Code name: Exasol SaaS, Python 3.10, Security Fixes

## Summary

This release adds support for parameters for SaaS instances of Exasol database to the configuration page.

Additionally, this release fixes the following vulnerabilities by updating dependencies:
* Vulnerability CVE-2024-23342 in transitive dependency via `localstack` to `ecdsa` vulnerably to Minerva timing attack on P-256 in `python-ecdsa`.
* Vulnerability CVE-2024-5206 in dependency `scikit-learn` versions below `1.5.0` caused by sensitive data leakage.

The release ignores the following vulnerabilities
* Ignoring vulnerability CVE-2024-33663 in transitive dependency via `localstack` to `python-jose` `3.3.0` caused by algorithm confusion with OpenSSH ECDSA keys as there is no newer version of `python-jose` available and the dependency only affects tests.
* Ignoring vulnerability CVE-2024-35195 in dependency `requests` in versions below `2.32.0` caused by requests `Session` object not verifying requests after making first request with `verify=False` as `requests` in version `2.32.0` and higher are incompatible with docker-compose.
* Ignoring vulnerability CVE-2024-37891 in transitive dependency via `boto3` to `urllib3` in versions below `2.2.2` caused by proxy-authorization request header not to be stripped during cross-origin redirects as no update of notebook-connector is available, yet.

Additionally the release updates the operating system from ubuntu 20.04 to 22.04 and Python version to 3.10 in the published images for Docker, AMI, and virtual machines.

## AI-Lab-Release

Version: 2.1.0

## Features

* 277 Added the SaaS database parameters to the configuration page.
* 279 Made the notebooks tests running in SaaS as well as in the Docker-DB.

## Security

* #207 Fixed vulnerability CVE-2024-23342 by updating dependency ecdsa
* #298: Fixed vulnerabilities by updating dependencies

## Bug Fixes

n/a

## Documentation

* #249: Added a troubleshooting section to the user guide documenting died kernel for transformers/te_init.ipynb.
* #284: Improved User Guide regarding Docker volumes

## Refactoring

* #267: Switched CodeBuildWaiter to use tenacity
* #276: Started using the new ITDE Manager interface in the notebook-connector 0.2.9
* #282: Updated python version to Python 3.10
* #295: Made notebook-tests mandatory for merge
* #193: Ignored warnings in notebook tests
* #297: Reduced log level for transitive libraries in notebook tests
