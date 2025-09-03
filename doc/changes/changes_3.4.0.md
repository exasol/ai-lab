# AI-Lab 3.4.0 released <TBD>

Code name: Support GPU usage in AWS EC2 instances

## Summary

This release add support for arbitrary AWS EC2 instance types (e.g. T4 GPU) and AWS Machine Images (AMI).

See the related CLI commands in the Developer Guide
* `create-vm`
* `setup-ec2`
* `setup-ec2-and-install-dependencies`

The release also merges the developer CLI commands `setup-ec2-and-install-dependencies` and `setup-ec2` into the new combined command `start-ec2` with option `--install-dependencies`.

## Features

* #376: Added support for arbitrary AWS EC2 instance types, e.g. T4 GPU
* #379: Updated AI Lab version in user guide and developer guide
* #380: Updated version of PTB actions used in GitHub workflows
* #381: Supported using arbitrary AWS machine images (AMI)
* #386: Simplified developer commands
* #374: Added GPU option to Jupyter UI

## Refactorings

* #377: Adjusted SLC notebooks to new interface
* #397: Upgraded to notebook-connector 2.0.0
* #399: Use model installation function from notebook-connector for transformer notebooks

## Bug Fixes

* #392: Fixed automatic start of Jupyterlab in EC2
