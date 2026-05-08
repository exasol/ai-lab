# AI-Lab 5.1.0 released 2026-05-08

Code name: Security Dependency Updates

## Summary

This release fixes multiple security vulnerabilities in dependencies and upgrades the project to Python 3.11.

## Security Issues

* Fixed CVE-2025-14010 (ansible) by upgrading from `^10.7.0` to `^12.2.0`
* Fixed CVE-2025-71176 (pytest) by upgrading from `>=8.3.2` to `>=9.0.3`
* Fixed CVE-2026-33441 (mistune) by pinning to `>=3.2.1`
* Fixed CVE-2026-39377 and CVE-2026-39378 (nbconvert) by pinning to `>=7.17.1`

## Refactorings

* Upgraded minimum Python version from 3.10 to 3.11 (required by ansible >=12)
* Updated CI/CD workflows and AWS CodeBuild specs to use Python 3.11
* Removed `pytest-check-links` dependency (incompatible with pytest >=9)
* Updated ansible virtualenv tasks to use `python3.11`
