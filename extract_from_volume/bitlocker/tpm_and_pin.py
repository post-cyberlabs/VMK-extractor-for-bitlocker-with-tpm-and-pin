
from hashlib import sha256
from binascii import hexlify, unhexlify
from Cryptodome.Cipher import AES

from .structure.block import FveBlock
from .structure.entry import FveEntry
from .structure.constant import EntryType, EntryValueType, KeyProtectionType
from .structure.entries import VolumeMasterKey


class BitLockerTPMwithPIN:
    block: FveBlock = None
    def __init__(self, block):
        self.block = block
    
    def get_vmk_for_TPM_with_PIN(self) -> VolumeMasterKey:
        for entry in self.block.entries:
            if entry.entry_type is not EntryType.VMK or entry.value_type is not EntryValueType.VOLUME_MASTER_KEY:
                continue
            vmk: VolumeMasterKey = entry.loaded_data
            if vmk.protection_type is KeyProtectionType.TPM_WITH_PIN:
                return vmk
        raise ValueError("Unable to find VMK for TPM with PIN :/")

    def get_salt_for_key1(self) -> bytes:
        result = None
        vmk = self.get_vmk_for_TPM_with_PIN()
        for property in vmk.properties:
            if property.entry_type is EntryType.PROPERTY and property.value_type is EntryValueType.STRETCH_KEY and property.size == 0X6C:
                return property.data[4:20]
        raise ValueError("Unable to find salt for key1")

    def generate_key1(self, pin: str):
        """Generate KEY 1 
        """
        data = bytearray(b'\x00' * 0x20)

        data += bytearray(sha256(sha256(pin.encode('UTF-16LE')).digest()).digest())
        data += bytearray(self.get_salt_for_key1())

        data += bytearray(b'\x00' * 0x8)

        assert len(data) == 0x58

        for idx in range(0x100000):
            data = bytearray(sha256(bytes(data)).digest()) + data[0x20:]
            for idx in range(8):
                new = data[0x50 + idx] + 1
                if new > 0xFF:
                    data[0x50 + idx] = 0
                else:
                    data[0x50 + idx] = new
                    break
        return bytes(data[:0x20])
    
    def decode_key_protector_container(self, key, encoded_KP_from_tpm):
        encoded_data = FveEntry.load_from_data(encoded_KP_from_tpm)
        cipher = AES.new(key, AES.MODE_CCM, nonce=encoded_data.loaded_data.nonce)
        return cipher.decrypt(encoded_data.loaded_data.encrypted_data)
    
    def get_encrypted_VMK(self) -> bytes:
        encrypted_data : FveEntry = None
        vmk = self.get_vmk_for_TPM_with_PIN()
        for idx in range(len(vmk.properties)):
            property = vmk.properties[idx]
            if property.entry_type is EntryType.PROPERTY and property.value_type is EntryValueType.UNK13:
                encrypted_data = vmk.properties[idx+1]
        return encrypted_data.raw

    def get_encrypted_FVEK(self):
        for entry in self.block.entries:
            if entry.entry_type is EntryType.FKEV or entry.value_type is EntryValueType.AES_CCM_ENCRYPTED_KEY:
                return entry.raw
        raise ValueError("Unable to find encrypted FVEK :/")
    
    def get_encrypted_autounlock(self):
        for entry in self.block.entries:
            if entry.entry_type is EntryType.AUTO_UNLOCK or entry.value_type is EntryValueType.AES_CCM_ENCRYPTED_KEY:
                return entry.raw
        raise ValueError("Unable to find encrypted Auto unlock :/")