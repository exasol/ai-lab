
default_config = {
    "time_to_wait_for_polling": 10.0,
    # Source AMI is set to Ubuntu 20.04
    "source_ami_id": "ami-0c9354388bb36c088"
}


class ConfigObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


global_config = ConfigObject(**default_config)

