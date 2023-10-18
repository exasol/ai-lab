DEFAULT_TAG_KEY = "exa_slc_id"


def create_default_asset_tag(value: str) -> list:
    return [
                {
                    'Key': DEFAULT_TAG_KEY,
                    'Value': value
                },
            ]
