import click

aws_options = [
    click.option('--aws-profile', required=False, type=str,
                 help="Id of the AWS profile to use."),
]
