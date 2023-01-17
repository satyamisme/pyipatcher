import click
from pyipatcher.patchfinder.patchfinder64 import patchfinder64
import pyipatcher.patchfinder.kernelpatchfinder as kpf

kernel_vers = 0

@click.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
@click.option(
    '-a',
    '--amfi',
    'patch_amfi',
    is_flag=True,
    help='Patch AMFI'
)
@click.option(
    '-e',
    '--rootvol-seal',
    'rootvol_seal',
    is_flag=True,
    help='Patch root volume seal is broken (iOS 15 Only)'
)
@click.option(
    '-u',
    '--update-rootfs-rw',
    'update_rootfs_rw',
    is_flag=True,
    help='Patch update_rootfs_rw (iOS 15 Only)'
)

def kernelpatcher(input, output, patch_amfi, rootvol_seal, update_rootfs_rw):
    kernel = input.read()
    if kernel[:4] == b'\xca\xfe\xba\xbe':
        click.echo('Detected fat macho kernel')
        kernel = kernel[28:]
    pf = patchfinder64(kernel)
    xnu = pf.get_str(b"root:xnu-", 4, end=True)
    global kernel_vers
    kernel_vers = int(xnu)
    print(f"Kernel-{kernel_vers} inputted")
    if patch_amfi:
        click.echo('Getting get_amfi_out_of_my_way_patch()')
        kpf.get_amfi_out_of_my_way_patch(pf)
    if rootvol_seal:
        click.echo('Getting get_root_volume_seal_is_broken_patch()')
        kpf.get_root_volume_seal_is_broken_patch(pf)
    if update_rootfs_rw:
        click.echo('Getting get_update_rootfs_rw_patch()')
        kpf.get_update_rootfs_rw_patch(pf)
    click.echo(f'Writing out patched file to {output.name}')
    output.write(pf._buf)
