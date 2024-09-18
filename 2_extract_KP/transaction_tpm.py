#!/usr/bin/env python3
import csv
import binascii
import click
from binascii import hexlify, unhexlify
from typing import List
from tpmstream.io.binary import Binary
from tpmstream.io.pretty import Pretty
from tpmstream.spec.commands import Command, Response
from tpmstream.common.object import events_to_obj,events_to_objs

class Transaction:
    command_raw : bytes = None
    command : Command = None 
    response_raw : bytes = None
    response : Response = None
    def __init__(self, command_raw : bytes, response_raw : bytes) -> None:
        self.command_raw = command_raw
        self.response_raw = response_raw

        events = Binary.marshal(tpm_type=Command, buffer=command_raw)
        self.command = events_to_obj(events)

        events = Binary.marshal(tpm_type=Response, buffer=response_raw, command_code=self.command.commandCode)
        self.response = events_to_obj(events,command_code=self.command.commandCode)
    def __repr__(self) -> str:
        return f"""Transaction:
    CommandCode  : {self.command.commandCode}
    Command raw  : {hexlify(bytes(self.command_raw)).decode('utf-8')}
    Response raw : {hexlify(bytes(self.response_raw)).decode('utf-8')}
    """

class TPMTransactionPulseView:
    transactions : List[Transaction] = None 
    def __init__(self, csv_file):
        with open(csv_file) as csvfile:
            reader = csv.reader(csvfile)
            self.data = list(reader)
        self._load_message()

    def get_read_fifo_at_index(self, index):
        if index + 2 > len(self.data):
            return None
        if self.data[index][2] != "Read":
            return None
        if self.data[index + 1][2] != "Register: TPM_DATA_FIFO_0":
            return None
        return int(self.data[index + 2][2], 16)

    def get_write_fifo_at_index(self, index):
        if index + 2 > len(self.data):
            return None
        if self.data[index][2] != "Write":
            return None
        if self.data[index + 1][2] != "Register: TPM_DATA_FIFO_0":
            return None
        return int(self.data[index + 2][2], 16)

    @staticmethod
    def gather_message(raw_extraction_message):
        messages = []
        tmp_buffer = []
        for msg in raw_extraction_message:
            if msg[0] == 0x80 and msg[1] in [0x01, 0x02]:
                if len(tmp_buffer) > 0:
                    messages.append(tmp_buffer)
                    tmp_buffer = []
            tmp_buffer.extend(msg)
        if tmp_buffer != b'':
            messages.append(tmp_buffer)
        return messages

    def _load_message(self):
        ungrouped_messages_read_fifo = []

        idx = 0
        while idx < len(self.data):
            if self.get_read_fifo_at_index(idx) is not None:
                buffer = []
                fifo_loop = True
                while fifo_loop:
                    value = self.get_read_fifo_at_index(idx)
                    if value is None:
                        fifo_loop = False
                        #print("Debug Buffer FIFO: %s" % binascii.hexlify(bytes(buffer)).decode('utf-8'))
                        ungrouped_messages_read_fifo.append(buffer)
                    else:
                        buffer.append(value)
                        idx += 3
            idx += 1

        ungrouped_messages_write_fifo = []

        idx = 0
        while idx < len(self.data):
            if self.get_write_fifo_at_index(idx) is not None:
                buffer = []
                fifo_loop = True
                while fifo_loop:
                    value = self.get_write_fifo_at_index(idx)
                    if value is None:
                        fifo_loop = False
                        #print("Debug Buffer FIFO: %s" % binascii.hexlify(bytes(buffer)).decode('utf-8'))
                        ungrouped_messages_write_fifo.append(buffer)
                    else:
                        buffer.append(value)
                        idx += 3
            idx += 1


        self.messages_read_fifo = self.gather_message(ungrouped_messages_read_fifo)
        self.messages_write_fifo = self.gather_message(ungrouped_messages_write_fifo)

        self.transactions = []
        for idx in range(len(self.messages_read_fifo)):
            self.transactions.append(Transaction(self.messages_write_fifo[idx], self.messages_read_fifo[idx]))

    def __repr__(self) -> str:
        output = [] 
        for transac in self.transactions:
            output.append(repr(transac))
        return "\n".join(output)

@click.command()
@click.argument('csv_file', type=click.Path(exists=True, dir_okay=False))
def main(csv_file):
    """Extract TPM transaction data of CSV file that are come from PulseView SPI decoder
    """
    transaction = TPMTransactionPulseView(csv_file)
    print(transaction)

if __name__ == "__main__":
    main()
