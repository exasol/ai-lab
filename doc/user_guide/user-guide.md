# AI Lab User Guide

Exasol AI Lab is available in multiple editions as shown in the following table.

Please see common [system requirements](system-requirements.md) for all editions and select your favorite edition depending on your operating system, infrastructure, administrative permissions, and technical skills.

Recommendations
* If you have an AWS account then Exasol recommends using the AMI Edition running the AMI image in an AWS EC2 instance.
* In case a Docker client is available on your system then probably the Docker Edition is the best choice.
* When you want to use the VM Edition then select an appropriate VM image format depending on the Hypervisor software available on your system.

| Edition                                           | Image(s)                                                                 |
|---------------------------------------------------|--------------------------------------------------------------------------|
| [AMI Edition](ami-usage.md)                       | Amazon Machine Image (AMI)                                               |
| [Docker Edition](docker/docker-usage.md)          | Docker Image                                                             |
| [Virtual Machine Edition](vm-edition/vm-usage.md) | VMware Virtual Machine Disk (VMDK), Virtual Hard Disk by Microsoft (VHD) |

Each image contains all necessary dependencies and automatically launches Jupyterlab when booting or running the image.

Please
* [Download](https://github.com/exasol/ai-lab/releases/latest) your favorite image from the latest AI Lab release on GitHub,
* Run the AI Lab as described in the resp. documentation for the edition, and
* Connect to AI Lab's [Jupyter Service](https://github.com/exasol/ai-lab/blob/4.0.0/doc/user_guide/jupyter.md).

In case of problems, please refer to our [Troubleshooter](troubleshooting.md).
