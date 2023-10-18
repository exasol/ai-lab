from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.tags import DEFAULT_TAG_KEY

LOG = get_status_logger(LogType.EXPORT)


def run_make_ami_public(aws_access: AwsAccess, asset_id: AssetId):
    """Modifies all AMI's with matching asset-id so that they become publicly available."""
    amis = aws_access.list_amis(filters=[{'Name': f'tag:{DEFAULT_TAG_KEY}', 'Values': [asset_id.tag_value]}])
    LOG.info(f"Found {len(amis)} for asset-id {asset_id}")
    make_public_launch_permission = {
        'Add': [
            {
                'Group': 'all',
            },
        ],
    }
    private_amis = (ami for ami in amis if not ami.is_public)
    for ami in private_amis:
        LOG.info(f"Making {ami.id} public.")
        aws_access.modify_image_launch_permission(ami.id, make_public_launch_permission)
        new_ami = aws_access.get_ami(ami.id)
        if not new_ami.is_public:
            raise RuntimeError(f"Making AMI {ami.id} public did not work")
