import click

aws_options = [
    click.option(
        '--aws-profile', required=False, type=str, metavar="PROFILE",
        help="Id of the AWS profile to use."
    ),
]
