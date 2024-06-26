from importlib_metadata import version

# name of the project as specified in file pyproject.toml
AI_LAB_VERSION = version("exasol-ai-lab")

_default_config = {
    "time_to_wait_for_polling": 10.0,
    # Source AMI is set to Ubuntu 22.04. Owner id '099720109477' == 'Canonical'
    "source_ami_filters": {
        "name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*",
        "owner-id": "099720109477",
        "architecture": "x86_64",
        "state": "available"
    },
    "ai_lab_version": AI_LAB_VERSION,
    "waf_region": "us-east-1"
}


class ConfigObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


default_config_object = ConfigObject(**_default_config)
