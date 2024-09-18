#!/usr/bin/env python3
import click
from bitlocker.utils import *
from bitlocker.structure.header import FveHeader

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--volume', prompt='Targeted volume', help='Target bitlocker volume')
@click.option('--block-id', help='Block id (must be between 1 and 3)', default=1)
def main(volume, block_id):
    if not is_bitlocker_volume(volume):
        raise TypeError(f"volume {volume} is not in NTFS")
    else:
        click.echo(f"{volume} is a bitlocker volume")

    res = get_fve_block_offset(volume)
    click.echo("Block offset: %s" % ", ".join([hex(i) for i in res]))

    header = FveHeader.load_from_volume(volume, block_id-1)
    click.echo(header.block)
    
if __name__ == "__main__":
    main()