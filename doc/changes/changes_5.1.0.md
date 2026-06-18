# AI-Lab 5.1.0 released 2026-06-03

Code name: SageMaker Notebook Removal, Ansible-Runner-Wrapper, CI/CD now on Github Action

## Summary

This release removes the SageMaker Notebooks. Furthermore, it replaces the former ansible wrapper in the AI Lab by external dependency to `ansible-runner wrapper` and the CI/CD workflows moved from AWS CodeBuild to Github Actions

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
* #530: Migrated notebook deployment to Notebook Connector and removed the repo-local notebook source tree

## Bug Fixes

* #522: Fixed AWS CodeBuild issue with Ansible inventory group name
* #523: Fixed docker image build issue with rsync package pin to ubuntu version
