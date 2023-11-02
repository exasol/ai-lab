import click

from exasol.ds.sandbox.lib.config import SLC_VERSION

id_options = [
              click.option('--asset-id', type=str, default=SLC_VERSION,
                           help="This value will be used in the AMI name, as tag on all AWS resources "
                                "and in the prefix of the S3 objects.")
]
