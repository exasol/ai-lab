def release_version_from_tag(release_tag: str) -> str:
    release_version = release_tag.removeprefix("refs/tags/")
    if release_version.startswith("v"):
        raise ValueError("Release tags must be bare versions without a leading 'v'.")
    return release_version
