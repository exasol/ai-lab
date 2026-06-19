# AI-Lab 6.0.0 released 2026-06-19

Code name: Notebook Connector 3.0.0, SageMaker Notebook Removal

## Summary

This release uses [exasol-notebook-connector 3.0.0](https://github.com/exasol/notebook-connector/releases/tag/3.0.0) and removes the remaining SageMaker notebooks. The notebooks are now hosted in the [notebook-connector](https://github.com/exasol/notebook-connector/tree/3.0.0/exasol/nb_connector/resources/notebooks).

## Features

* #518: Removed Sagemaker tests from CI testing pipeline

## Documentation

* #519: Removed Sagemaker mentions from jupyter notebooks

## Refactorings

* #504: Replaced `exasol.ds.sandbox.lib.ansible` by `ansible-runner-wrapper`
* #515: Migrated AI-Lab release from AWS Codebuild to Github Actions
* #521: Removed some Ansible unit tests
* #525: Moved the release workflow into the package CLI layer and removed the legacy release script tree
* #526: Migrated the AWS-backed CI from CodeBuild to GitHub Actions
* #530: Migrated notebook deployment to Notebook Connector 3.0.0 from PyPI and removed the repo-local notebook source tree

## Bug Fixes

* #522: Fixed AWS CodeBuild issue with Ansible inventory group name
* #523: Fixed docker image build issue with rsync package pin to ubuntu version
