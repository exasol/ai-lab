# ai-lab 0.2.0, released 2024-02-15

Code name: Post release fixes

## Summary

This release comes with a number of updates and improvements and enhanced and fixed documentation.

Additionally the release fixes vulnerabilities by updating dependencies in file `poetry.lock` and Ansible files.

## AI-Lab-Release

Version: 0.2.0

## Features

## Security

* #187: Fixed vulnerabilities by updating dependencies
  * `ansible` from 6.7.0 to 7.7.0 to fix CVE-2023-5115, CVE-2022-3697.
  * `ansible-core` from 2.13.13 to 2.14.14 to fix CVE-2024-0690, CVE-2023-5764.
  * `urllib3` from 1.26.16 to 1.26.18 to fix CVE-2023-45803, CVE-2023-43804.
  * `tornado` from 6.3.2 to 6.4 to fix vulnerability to HTTP request smuggling via improper parsing of `Content-Length` fields and chunk lengths.
  * `paramiko` from 3.2.0 to 3.4.0 to fix CVE-2023-48795.
  * `jupyterlab` from 4.0.6 to 4.1.1 to fix CVE-2024-22420, CVE-2024-22421.
  * `jinja2` from 3.1.2 to 3.1.3 to fix CVE-2024-22195.
  * `gitpython` from 3.1.31 to 3.1.41 to fix CVE-2024-22190, CVE-2023-41040, CVE-2023-40590, CVE-2023-40267.
  * `cryptography` from 41.0.1 to 42.0.2 to fix CVE-2023-50782, CVE-2023-49083, CVE-2023-38325.
  * `certifi` from 2023.5.7 to 2024.2.2 to fix CVE-2023-37920.
  * `requests` from 2.25.1 to 2.31.0 to fix CVE-2023-32681.

## Bug Fixes

* #163: Fixed version number of VM images etc.
* #161: Fixed the bug in the Transformers' Translation notebook.

## Documentation

* #125: Explained login to docker container
* #174: Added to FAQ: How to install additional python packages into the Docker container

## Refactoring

* #160: Implemented the PM's recommendations of 2024-01-24.
* #120: Passing the secret store object (sb_config) as a parameter to all functions that need it.
* #165: Reduced log output in Codebuild ai-lab
* #184: Changed notebook tests to only run if the commit message contains a special string
* #167: Replacing the term "Docker-DB" with "Exasol Docker-DB" in all notebooks and documentation.
* #168: Renaming the section name “Access Configuration” to "Open Secure Configuration Storage".
* #170: Renaming the section name "Set up" to "Setup".
* #182: Renaming the secret store global variable from "sb_config" to "ai_lab_config".
* #169: Renaming the default database schema from "IDA" to "AI_LAB".
* #128: Removed unused dependencies
* #188: Start using the new namespace of the notebook-connector 0.2.7.
