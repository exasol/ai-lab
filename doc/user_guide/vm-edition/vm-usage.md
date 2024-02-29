# AI-Lab Virtual Machine Edition

The AI-Lab Virtual Machine Edition offers two different VM images
* VMware Virtual Machine Disk (VMDK)
* Virtual Hard Disk by Microsoft (VHD)

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

## Instructions for specific operating systems and hypervisors

* [Boxes (QEMU) on Linux operating system](qemu.md)
* [Importing image format VMDK into Oracle Virtual Box on Windows](win-vbox.md)

## Login

See [Log in to AMI and VM Editions](../login-vm-and-ami.md) for logging into the system.
