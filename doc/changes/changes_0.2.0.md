# ai-lab 0.2.0, released 2024-02-15

Code name: Post release fixes

## Summary

This release comes with a number of updates and improvements and enhanced and fixed documentation.

## AI-Lab-Release

Version: 0.2.0

## Features

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
