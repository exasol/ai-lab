# Data Science Sandbox Developer Guide

## Overview

The overall idea of this project is to set-up an AWS EC-2 instance, using cloudformation templates, then install all
dependencies via _Ansible_, generate an AMI image based on the final EC-2 instance, and finally export the AMI image to
the virtual image formats.

## Requirements

This package requires:

* Python (>=3.8)
* Poetry (>=1.2.0)
* Docker (for integration tests)
* AWS CLI

## Setup

### Install githooks

Run the following command before development.

```shell
cd githooks
bash install.sh
```

## Design Goals

The Data Science Sandbox (DSS) uses AWS as backend, because it provides the possibility to run the whole workflow during
a ci-test.

This project uses

* `boto3` to interact with AWS
* `pygithub` to interact with the Github releases
* `ansible-runner` to interact with Ansible.
  Proxy classes to those projects are injected at the CLI layer. This allows to inject mock classes in the unit tests.
  A CLI command has normally a respective function in the `lib` submodule. Hence, the CLI layer should not contain any
  logic, but invoke the respective library function only. Also, the proxy classes which abstract the dependant packages
  shall not contain too much logic. Ideally they should invoke only one function to the respective package.

Script `start-test-release-build` requires environment variable `GH_TOKEN` to contain a valid token for access to Github.

## Table of Contents

1. [AWS Build and Release Workflow](aws.md)
2. [Command Line Usage](commands.md)
3. [Testing](testing.md)
4. [Running tests in the CI](ci.md)
5. [Updating Packages](updating_packages.md)
