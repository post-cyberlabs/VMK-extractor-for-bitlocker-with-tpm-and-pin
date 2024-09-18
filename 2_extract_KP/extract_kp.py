#!/usr/bin/env python3
import click
from binascii import hexlify
from transaction_tpm import TPMTransactionPulseView
from tpmstream.spec.structures.constants import TPM_CC

@click.command()
@click.argument('csv_file', type=click.Path(exists=True, dir_okay=False))
def main(csv_file):
    """Extract TPM transaction data of CSV file that are come from PulseView SPI decoder
    """
    transaction_pulseview_output = TPMTransactionPulseView(csv_file)
    
    for transaction in transaction_pulseview_output.transactions:
        if transaction.command.commandCode == TPM_CC.Unseal:
            break
    click.echo(transaction)
    click.echo("Encrypted KP from TPM: ", nl=False)
    click.secho(hexlify(bytes(transaction.response.parameters.outData.buffer)).decode('utf-8'), bold=True, reverse=True)

if __name__ == "__main__":
    main()
