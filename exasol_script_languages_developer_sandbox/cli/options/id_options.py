import click
from importlib_metadata import version

DEFAULT_ID = version("exasol_script_languages_release")

id_options = [
              click.option('--asset-id', type=str, default=DEFAULT_ID,
                           help="This value will be used in the AMI name, as tag on all AWS resources "
                                "and in the prefix of the S3 objects.")
]
