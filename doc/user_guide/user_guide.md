# Data Science Sandbox User Guide

## Overview

Exaol AI-Lab can be used to explore AI applications on top of Exasol database.

The AI-Lab is available in multiple editions involving different technology stacks.

Depending on your operating system, infrastructure, administrative permissions, and technical skills, you might have specific constraints and preferences.

See [AI-Lab Editions](editions.md) to select your favorite edition.

## System Requirements

The editions of the AI-Lab have common requirements to be available on your system:
* CPU Architecture: x86
* CPU cores: minimum 1, recommended 2 cores
* Main memory (RAM): minimum 2 GiB, recommended 8 GiB
* Network access
* Recommend access to a running instance of Exasol database, otherwise you can start a small Exasol Docker DB
  * Please note: AI-Lab currently does not support Exasol SaaS.

As the AI-Lab is meant to explore AI applications on top of Exasol database, you, of course, need an instance of Exasol database running and be able to connect to it.

AI-Lab can automatically launch such an instance on demand. However when using AI-Lab's Docker Edition there are [additional constraints](docker/docker_usage.md#enabling-exasol-ai-lab-to-use-docker-features).

## Login to AMI and VM Editions

Username: **ubuntu**

At the first login to the sandbox (image or AMI) you will be prompted to change your password.
The default password is: **dss**

However, we suggest to use ssh-keys for the connection. When you use the AWS AMI, this will work automatically. When using the VM images, you need to deploy your ssh-keys. After you enabled ssh-keys, we recommend to disable ssh password authentication:
```shell
sudo sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
sudo systemctl restart ssh.service
```

## Connecting to Jupyter Service

Root location
* For Exasol AI-Lab's VM and AMI editions the root location is `$ROOT=/home/ubuntu`.
* For the Docker edition the root location is `$ROOT=/root`.

| Item                | Location or value                        |
|---------------------|------------------------------------------|
| Virtual environment | location `/$ROOT/jupyterenv`             |
| Location notebooks  | location `/$ROOT/notebooks`              |
| Password            | `dss`                                    |
| Http Port           | `49494` (or the port you forwared it to) |

Exasol strongly recommends to change the Jupyter password as soon as possible. Details about how to do that will be shown in the login screen.

Check [Jupyter Home](https://jupyter.org/) for more information.

You can open the starting page with `https://<host>:<port>`.

Please note specific instructions for [AI-Lab Docker Edition](docker/docker_usage.md).
