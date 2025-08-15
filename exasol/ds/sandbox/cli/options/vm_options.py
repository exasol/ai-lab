import click

from exasol.ds.sandbox.lib.export_vm.vm_disk_image_format \
    import VmDiskImageFormat

vm_options = [
    click.option(
        '--vm-image-format', multiple=True, show_default=True,
        default=VmDiskImageFormat.default_formats(),
        type=click.Choice(VmDiskImageFormat.all_formats()),
        help="The VM image format. Can be declared multiple times."
    ),
    click.option(
        '--no-vm', is_flag=True,
        help="If set, no vm image will be exported. "
        "This option takes precedence over 'vm-image-format'."
    )
]
