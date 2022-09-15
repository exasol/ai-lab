class AssetId:
    def __init__(self, asset_id: str, stack_prefix="EC2-SLC-DEV-SANDBOX-", ami_prefix="Exasol-SLC-Developer-Sandbox"):
        self._asset_id = asset_id
        self._stack_prefix = stack_prefix
        self._ami_prefix = ami_prefix

    @property
    def tag_value(self):
        return self._asset_id

    @property
    def bucket_prefix(self):
        return f"{self.BUCKET_PREFIX}/{self._asset_id}"

    @property
    def ami_name(self):
        return f"{self._ami_prefix}-{self._asset_id}"

    @property
    def stack_prefix(self):
        return f"{self._stack_prefix}-{self._asset_id}".replace("_", "-").replace(".", "-").replace(" ", "-")

    def __repr__(self):
        return self._asset_id

    BUCKET_PREFIX = "slc_developer_sandbox"
