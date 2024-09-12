from struct import unpack
from binascii import hexlify
from datetime import datetime

class AesCcmEncryptedKey:
    def __init__(self, data) -> None:
        self.nonce = data[:12]
        self.nonce_time = datetime.fromtimestamp(unpack("<Q", data[:8])[0]/ 10000000 - 11644473600)
        self.nonce_counter = unpack("<I",data[8:12])[0]
        self.encrypted_data = data[12+16:]
    def __repr__(self) -> str:
        return f"""AesCcmEncryptedKey
    - Nonce: {hexlify(self.nonce).decode('utf-8')}
    - Nonce counter: {hex(self.nonce_counter)}
    - Nonce time: {self.nonce_time}
    - Encrypted data: {hexlify(self.encrypted_data).decode('utf-8')}"""