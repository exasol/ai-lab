import click

from exasol.ds.sandbox.lib.config import AI_LAB_VERSION

id_options = [
    click.option(
        '--asset-id', type=str, default=AI_LAB_VERSION, metavar="ID",
        help="This value will be used in the AMI name, as tag on all AWS resources "
        "and in the prefix of the S3 objects.")
]
