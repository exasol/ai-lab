# AI-Lab Editions

Exasol AI-Lab is available in the multiple editions as shown in the following table.

Please see common [system requirements](system-requirements.md) for all editions and select your favorite edition depending on your operating system, infrastructure, administrative permissions, and technical skills.

Recommendations
* If you have an AWS account then Exasol recommends to use the AMI Edition running the AMI image in an AWS EC2 instance.
* In case a Docker client is available on your system then probably the Docker Edition is the best choice.
* When you want to use the VM Edition then select an appropriate VM image format depending on the Hypervisor software available on your system.


| Description                              | Format(s)                                                                |
|------------------------------------------|--------------------------------------------------------------------------|
| [AMI Edition](ami-usage.md)              | Amazon Machine Image (AMI)                                               |
| [Docker Edition](docker/docker-usage.md) | Docker Image                                                             |
| [Virtual Machine Edition](vm-usage.md)   | VMware Virtual Machine Disk (VMDK), Virtual Hard Disk by Microsoft (VHD) |

Each of the editions is associated with an _image_ in a specific format which
* Is linked in the [release notes](https://github.com/exasol/ai-lab/releases/latest) for download
* Contains all necessary dependencies
* Provides a running Jupyterlab instance which is automatically started when booting or running the image

