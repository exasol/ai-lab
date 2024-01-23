# Editions of Exasol AI-Lab

Exasol AI-Lab is available in the following editions:

<!--
| VMDK   | VMware Virtual Machine Disk    |
| VHD    | Virtual Hard Disk by Microsoft |
-->

| Description             | Format(s)                   |
|-------------------------|-----------------------------|
| Amazon Machine Image    | AMI                         |
| Virtual Machine Edition | VMDK, VHD                   |
| Docker Edition          | Docker Image |

Each of the editions is associated with an _image_ in a specific format which
* Is linked in the [release notes](https://github.com/exasol/data-science-sandbox/releases/latest) for download
* Contains all necessary dependencies
* Provides a running Jupyterlab instance which is automatically started when booting or running the image

## Selecting your Edition

Please see common [system requirements](user_guide.md#system-requirements) for all editions.

Recommendations
* If you have an AWS account then Exasol recommends to use the AMI image in an AWS EC2 instance.
* In case a Docker client is available on your system then probably the Docker Edition is the best choice.
* When you want to use one of the VM images then select an appropriate format depending on the Hypervisor software available on your system:

### AMI Edition

The ID of the AMI (Amazon Machine Image) is mentioned in the [release notes](https://github.com/exasol/data-science-sandbox/releases/latest) and can be used to start an EC2-instance in your AWS account.

The naming scheme is: "_Exasol-Data-Science-Sandbox-${VERSION}_", e.g. "_Exasol-Data-Science-Sandbox-5.0.0_"

See also [User Guide for AI-Lab AMI Edition](ami_usage.md).

### Virtual Machine Edition

Each release of Exasol AI-Lab provides two VM formats:

| Format     | Description                    |
| -----------|--------------------------------|
| VMDK       | VMware Virtual Machine Disk    |
| VHD        | Virtual Hard Disk by Microsoft |

The following table shows which Hypervisor supports which image formats:

| Hypervisor          | VMDK | VHD |
|---------------------|------|-----|
| VMWare work station | yes  | ?   |
| Virtual box         | yes  | yes |
| Hyper-V             | ?    | yes |
| WSL 2               | ?    | ?   |

Notes for Hypervisors based on KVM/[QEMU](https://en.wikipedia.org/wiki/QEMU):
* There multiple alternative UIs, see https://en.wikipedia.org/wiki/Libvirt#User_Interfaces.
* File in format VHD or VMDK needs to be converted first, see
  * https://docs.openstack.org/image-guide/convert-images.html
   * https://linux.die.net/man/1/qemu-img

See also [User Guide for AI-Lab VM Edition](vm_usage.md).

### Docker Edition

The Docker image is published to DockerHub at https://hub.docker.com/r/exasol/data-science-sandbox.

See also [User Guide for AI-Lab Docker Edition](docker/docker_usage.md).
