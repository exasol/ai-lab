# AI-Lab 5.1.0 released 2026-05-19

Code name: Ansible Runner Wrapper dependency and Sagemaker tests removal

## Summary

This release replaces the former ansible wrapper in the AI Lab by external dependency to `ansible-runner wrapper`.
It also removes Sagemaker tests from CI testing pipeline.

## Features

* #518: Removed Sagemaker tests from CI testing pipeline

## Refactorings

* #504: Replaced `exasol.ds.sandbox.lib.ansible` by `ansible-runner-wrapper`.
