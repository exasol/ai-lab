import click

ec2_key_options = [
    click.option('--ec2-key-file', required=False, type=click.Path(exists=True, file_okay=True, dir_okay=False),
                 default=None,
                 help="The EC2 key-pair-file to use. If not given a temporary key-pair-file will be created."),
    click.option('--ec2-key-name', required=False, type=str,
                 default=None, help="The EC2 key-pair-name to use. Only needs to be set together with ec2-key-file.")
]

ec2_host_options = [
    click.option('--host-name', required=True, type=str,
                 help="The remote hostname on which the setup needs to be executed."),
    click.option('--ssh-private-key', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False),
                 help="The private key file which can be used to login to the server via ssh.")
]
