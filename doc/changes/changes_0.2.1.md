# ai-lab 0.2.1, released 2024-??-??

Code name: Fix Cloud Storage Notebook

## Summary

This release fixes the Cloud Storage notebook and also fixes vulnerabilities by updating dependencies in file `poetry.lock` and Ansible files.

Updating the dependencies required to upgrade the build environment from python 3.8 to 3.10. The Jupyterlab notebooks and their libraries remain on python 3.8 for now.

## AI-Lab-Release

Version: 0.2.1

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
  * `localstack` from 0.14.0 to 3.1.0 to fix CVE-2023-48054.

## Bug Fixes

* #205: Error on cloud storage notebook init

## Documentation

## Refactoring
