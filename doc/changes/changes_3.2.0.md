# AI-Lab 3.2.0 released 2025-??-??

Code name: Additional Updates on top of 3.1.0

## Summary

This release updates dependencies and fixes security vulnerabilities on top of 3.1.0.

Fixed vulnerabilities:

* Vulnerabilities in direct dependency `jinja2` version 3.1.4
  * #50 Moderate: Jinja has a sandbox breakout through malicious filenames Moderate
  * #49 Moderate: Jinja has a sandbox breakout through indirect reference to format method Moderate
* Vulnerabilities in transitive dependency `ansible-core` via `ansible`:
  * #44 Moderate, affects versions < 2.17.6, ansible-core Incorrect Authorization vulnerability Moderate
  * #47 Low, affects versions < 2.17.7: Ansible-Core vulnerable to content protections bypass Low
* Vulnerabilities in transitive testing dependency `tornado` version 6.4.1 via `pytest-check-links`,  `nbconvert`, `nbclient`, `jupyter-client`:
  * #46 High: Tornado has an HTTP cookie parsing DoS vulnerability High

Accepted vulnerabilities:

* Vulnerabilities in transitive testing dependency `python-jose` version 3.3.0 via `localstack` as there is no newer version available.
  * #31 Critical: python-jose algorithm confusion with OpenSSH ECDSA keys Critical
  * #32 Moderate: python-jose denial of service via compressed JWE content Moderate
* Vulnerabilities in transitive dependency `ansible-core` 2.17.7 version via `ansible` as there is no newer version available.
  * #43 High: Ansible vulnerable to Insertion of Sensitive Information into Log File High

## Security Issues

* #346: Dependency upgrade

## Refactorings

* #333: Added project short tag in notebook tests
* #339: Improved error reporting when the DockerDB doesn't start properly.

## Bug Fixes

 - #335: Fixed DNS resolution in ITDE when running jupyter notebook tests
 - #342: Updated the jupysql dependency to resolve the conflict with prettytable
