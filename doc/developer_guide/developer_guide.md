# Exasol AI Lab Developer Guide

## Overview

This guide covers the AI Lab project, its release flow, infrastructure, and development tooling.
The current release flow runs from a tag-triggered GitHub Actions workflow after PR CI validates the release logic.
GitHub Actions authenticates to AWS via OIDC for the AMI and VM build steps, and the workflow also publishes the
Docker edition.

## Table of Contents

1. [Requirements and Setup](dev-requirements-and-setup.md)
2. [Design Goals](design_goals.md)
3. [AWS Infrastructure Workflow](aws.md)
4. [Command Line Usage](commands.md)
5. [Testing](testing.md)
6. [Running tests in the CI](ci.md)
7. [Dependencies and Updating Packages](dependencies.md)
8. [Check for broken Hyperlinks](hyperlink-checking.md)
9. [Notebooks](notebooks.md)
10. [Developing the Docker Edition](docker.md)

Section [Dependencies](dependencies.md) is dedicated to enumerating all places defining dependencies as the AI Lab contains dependencies on multiple levels and specified in multiple places.
