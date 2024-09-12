from struct import unpack
from binascii import hexlify
from datetime import datetime
from ..constant import EncryptionMethod

class Key:
    encryption_method : EncryptionMethod = None
    def __init__(self, data) -> None:
        self.encryption_method = EncryptionMethod(unpack("<I",data[:4])[0])
        self.key_data = data[4:]
    def __repr__(self) -> str:
        return f"""Key
    - Encryption method: {self.encryption_method.name}
    - Key data: {hexlify(self.key_data).decode('utf-8')}"""