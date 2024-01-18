# Data Science Sandbox User Guide

## Overview

This project enables to create images, in different formats, which can be used to explore AI applications on top of Exasol database.

Exasol AI-Lab is available in multiple editions involving different technology stacks.  Depending on your operating system, infrastructure, administrative permissions, and technical skills, you might have specific constraints and preferences.

See [AI-Lab Editions](editions.md) to select your favorite edition.

<!--
### Usage

* [AMI Edition](ami_usage.md)
* [VM Edition](vm_usage.md)
* [Docker Edition](docker/docker_usage.md)
-->

## System Requirements

However, all editions of Exasol AI-Lab require a minimum hardware to be available on your system regarding
* CPU Architecture: x86
* CPU cores: minimum 1, recommended 2 Cores
* Main memory (RAM): minimum 2 GiB, recommended 8 GiB
* Network access
* Recommend access to a running instance of Exasol database, otherwise you can start a small Exasol Docker DB

As the Exasol AI-Lab is meant to explore AI applications on top of Exasol database, you, of course, need an instance of Exasol database running and be able to connect to it.

However, when using the AI-Lab Docker edition then Exasol AI-Lab in particular scenarios can automatically launch such an instance on demand, see [Enabling AI-Lab to use Docker features](docker/docker_usage.md#enabling-xai-to-user-docker-features) for details.

## Login to AMI and VM Editions

Username: **ubuntu**

At the first login to the sandbox (image or AMI) you will be prompted to change your password.
The default password is: **dss**

However, we suggest to use ssh-keys for the connection. When you use the AWS AMI, this will work automatically. When using the VM images, you need to deploy your ssh-keys. After you enabled ssh-keys, we recommend to disable ssh password authentication:
```shell
sudo sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
sudo systemctl restart ssh.service
```

## Connecting to Jupyter service

Root location
* For Exasol AI-Lab's VM and AMI editions the root location is `$ROOT=/home/ubuntu`.
* For the Docker edition the root location is `$ROOT=/root`.

| Item                | Location or value            |
|---------------------|------------------------------|
| Virtual environment | location `/$ROOT/jupyterenv` |
| Location notebooks  | location `/$ROOT/notebooks`  |
| Password            | `dss`                        |
| Http Port           | `8888`                       |

Exasol strongly recommends to change the Jupyter password as soon as possible. Details about how to do that will be shown in the login screen.

Check [Jupyter Home](https://jupyter.org/) for more information.
