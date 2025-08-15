import click

from exasol.ds.sandbox.lib.config import default_config_object

ec2_key_options = [
    click.option(
        '--ec2-key-file', required=False, default=None,
        type=click.Path(exists=True, file_okay=True, dir_okay=False),
        help="The EC2 key-pair-file to use. If not given a temporary key-pair-file will be created."
    ),
    click.option(
        '--ec2-key-name', required=False, type=str, default=None, metavar="NAME",
        help="The EC2 key-pair-name to use. Only needs to be set together with ec2-key-file."
    )
]

ec2_host_options = [
    click.option(
        '--host-name', required=True, type=str,
        help="The remote hostname on which the setup needs to be executed."
    ),
    click.option(
        '--ssh-private-key', required=True,
        type=click.Path(exists=True, file_okay=True, dir_okay=False),
        help="The private key file which can be used to login to the server via ssh."
    )
]

source_ami = default_config_object.source_ami_filters["name"]

ec2_instance_options = [
    click.option(
        '--ec2-instance-type', default="t2.medium", type=str,
        metavar="TYPE", show_default=True,
        help="EC2 instance type, e.g. t2.medium or g4dn.xlarge"
    ),
    click.option(
        '--ec2-source-ami', type=str, metavar="AMI-ID",
        help=f"""AWS Machine Image (AMI) to create the EC2 instance from.  If
        not specified, then ai-lab searches for the latest AMI matching
        {source_ami}."""
    )
]
