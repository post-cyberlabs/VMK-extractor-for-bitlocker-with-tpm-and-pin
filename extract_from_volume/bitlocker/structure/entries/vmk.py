import uuid
from typing import List
from datetime import datetime
from struct import pack,unpack
from ..constant import KeyProtectionType
from ...utils import reindent

class VolumeMasterKey:
    key_guid: uuid.UUID = None
    timestamp: datetime = None
    protection_type: KeyProtectionType = None
    properties: List = []

    def __init__(self, data) -> None:
        self.key_guid = uuid.UUID(bytes_le=data[:16])
        self.last_modification = datetime.fromtimestamp(unpack("<Q", data[16:24])[0]/ 10000000 - 11644473600)
        self.protection_type = KeyProtectionType(unpack("<H", data[26:28])[0])

    def __repr__(self) -> str:
        repr = f"""Volume Master Key:
    - Key identifier: {self.key_guid}
    - Last modification: {self.last_modification}
    - Protection type: 0x{self.protection_type.value:04X} {self.protection_type.name}
    - Properties (total: {len(self.properties)})"""
        for property in self.properties:
            repr += '\n'
            repr += reindent(str(property), 8)
        return repr