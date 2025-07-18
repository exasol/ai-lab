# AI-Lab 3.3.0 released 2025-07-18

Code name: Exasol Text AI and S3 Virtual schema notebooks

## Summary

This release adds notebooks for Exasol Text AI and the S3 Virtual schema extension. 
They provide capabilities to work with semi-structured and unstructed data. 

Additionally, this release fixes the following vulnerabilities by updating dependencies:
* CVE-2024-33663 in transitive dependency via `localstack` to `python-jose`
* CVE-2025-27516 in direct dependency `jinja2`
* CVE-2024-12797 in transitive dependency via `localstack`, `fabric`, `pygithub`, `ansible` to `cryptography`

## Features

* #344: S3 Virtual Schema installation and configuration
* #354: Added initialisation notebook for the Text AI.
* #363: Added preprocessing notebook for the Text AI.
* #369: Added analytics notebook for the Text AI.

## Refactorings

* #358: Updated to poetry 2.1.2 & switched GitHub runners to ubuntu-24.04

## Bug Fixes

