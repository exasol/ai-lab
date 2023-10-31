from enum import Enum
from typing import Tuple


class VmDiskImageFormat(Enum):
    """
    Contains supported VM image formats as described in
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.export_image
    """
    VMDK = "VMDK"
    RAW = "RAW"
    VHD = "VHD"


    @staticmethod
    def all_formats() -> Tuple[str, ...]:
        return tuple(vm_format.value for vm_format in VmDiskImageFormat)

    @staticmethod
    def default_formats() -> Tuple[str, ...]:
        return VmDiskImageFormat.VHD.value, VmDiskImageFormat.VMDK.value

