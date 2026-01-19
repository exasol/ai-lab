# Exasol AI Lab Developer Guide

## Overview

The overall idea of this project is to set-up an AWS EC-2 instance, using cloudformation templates, then install all
dependencies via _Ansible_, generate an AMI image based on the final EC-2 instance, and finally export the AMI image to
the virtual image formats.

## Table of Contents

1. [Requirements and Setup](dev-requirements-and-setup.md)
2. [Design Goals](design_goals.md)
3. [AWS Build and Release Workflow](aws.md)
4. [Command Line Usage](commands.md)
5. [Testing](testing.md)
6. [Running tests in the CI](ci.md)
7. [Dependencies and Updating Packages](dependencies.md)
8. [Check for broken Hyperlinks](hyperlink-checking.md)
9. [Notebooks](notebooks.md)
10. [Developing the Docker Edition](docker.md)

Section [Dependencies](dependencies.md) is dedicated to enumerating all places defining dependencies as the AI Lab contains dependencies on multiple levels and specified in multiple places.
