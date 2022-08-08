## Requirements

This package requires:
* Python (>=3.8)
* Docker (for integration tests)
* AWS CLI

## Overview

This packages aims to create a virtual machine image, in different formats, which can be used to build easily Exasol's script-languages-container, which are the runtime container for UDF's.
The idea is to setup an AWS EC-2 instance, using cloudformation templates, then install all dependencies via _Ansible_, generate an AMI image based on the final EC-2 instance, and finally export the AMI image to the virtual image formats.
The virtual machine image provides:
* The script-languages-release repositories
* All necessary dependencies to execute _exaslct_ in script-languages-release (This includes a correctly configured docker runtime)
* A running Jupyterlab instance which is automatically started during boot of the vm

