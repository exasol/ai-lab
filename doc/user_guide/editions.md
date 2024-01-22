# Editions of Exasol AI-Lab

Exasol AI-Lab is available in the following editions:

| Format | Description                    |
|--------|--------------------------------|
| VMDK   | VMware Virtual Machine Disk    |
| VHD    | Virtual Hard Disk by Microsoft |
| AMI    | Amazon Machine Image           |
| Docker | Image for Docker containers    |

Each of the editions is associated with an _image_ in a specific format which
* Is linked in the [release notes](https://github.com/exasol/data-science-sandbox/releases/latest) for download
* Contains all necessary dependencies
* Provides a running Jupyterlab instance which is automatically started when booting or running the image

## Selecting your Edition

Please see common [system requirements](user_guide.md#system-requirements) for all editions.

Recommendations
* If you have an AWS account then Exasol recommends to use the AMI image in an AWS EC2 instance.
* In case a docker client is available on your system then probably die Docker Edition is the best choice.
* When you want to use one of the VM images then select an appropriate format depending on the Hypervisor software available on your system:

| Hypervisor                                                                                      | VMDK | VHD |
|-------------------------------------------------------------------------------------------------|------|-----|
| VMWare work station                                                                             | yes  | ?   |
| Virtual box                                                                                     | yes  | yes |
| KVM/[QEMU](https://en.wikipedia.org/wiki/QEMU)/[Libvirt](https://en.wikipedia.org/wiki/Libvirt) | yes  | ?   |
| Hyper-V                                                                                         | ?    | yes |
| WSL 2                                                                                           | ?    | ?   |

For KVM/QEMU/libvirt there multiple alternative UIs, see https://en.wikipedia.org/wiki/Libvirt#User_Interfaces.

## AMI

The AMI ID is mentioned in the [release notes](https://github.com/exasol/data-science-sandbox/releases/latest) and can be used to start an EC2-instance in your AWS account.

The naming scheme is: "_Exasol-Data-Science-Sandbox-${VERSION}_", e.g. "_Exasol-Data-Science-Sandbox-5.0.0_"

See also [User Guide for AI-Lab AMI Edition](ami_usage.md).

## VM Image Formats

Each release of Exasol AI-Lab currently provides two VM formats:

| Format     | Description                    |
| -----------|--------------------------------|
| VMDK       | VMware Virtual Machine Disk    |
| VHD        | Virtual Hard Disk by Microsoft |

See also [User Guide for AI-Lab VM Edition](vm_usage.md).

## Image for Docker Containers

The Docker image is published to DockerHub at https://hub.docker.com/r/exasol/data-science-sandbox.

See also [User Guide for AI-Lab Docker Edition](docker/docker_usage.md).
