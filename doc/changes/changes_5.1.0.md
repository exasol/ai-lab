# AI-Lab 5.1.0 released 2026-05-28

Code name: Ansible Runner Wrapper dependency and Sagemaker tests removal

## Summary

This release replaces the former ansible wrapper in the AI Lab by external dependency to `ansible-runner wrapper`.
It also removes Sagemaker tests from CI testing pipeline and fixes AWS CodeBuild and Docker Image Build issues.

## Features

* #518: Removed Sagemaker tests from CI testing pipeline

## Documentation

* #519: Removed Sagemaker mentions from jupyter notebooks

## Refactorings

* #504: Replaced `exasol.ds.sandbox.lib.ansible` by `ansible-runner-wrapper`
* #515: Moved AI-Lab release CodeBuild from AWS to GitHub
* #521: Removed some Ansible unit tests

## Bug Fixes

* #522: Fixed AWS CodeBuild issue with Ansible inventory group name
* #523: Fixed docker image build issue with rsync package pin to ubuntu version
