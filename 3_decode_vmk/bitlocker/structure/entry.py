"""
typedef struct _FVE_ENTRY
{
	WORD		size;
	WORD		entry_type;
	WORD		value_type;
	WORD		version;
	CHAR		data[1];
} FVE_ENTRY, * PFVE_ENTRY;
"""
from struct import unpack
from binascii import hexlify
from ..utils import reindent
from .constant import EntryType,EntryValueType
from . import entries

class FveEntry:
    size:           int = None
    entry_type:     EntryType = None
    value_type:     EntryValueType = None
    version:        int = None
    data:         bytes = None
    raw:         bytes = None
    loaded_data: object = None

    def __init__(self, size, entry_type, value_type, version, data, raw=None):
        self.size = size
        self.entry_type = EntryType(entry_type)
        self.value_type = EntryValueType(value_type)
        self.version = version
        self.data = data
        self.raw = raw
        self._load_data()
    
    def _load_data(self):
        if self.entry_type is EntryType.VALIDATION and self.value_type is EntryValueType.VALIDATION:
            self.loaded_data = entries.Validation()
        elif self.entry_type is EntryType.DRIVE_LABEL and self.value_type is EntryValueType.UNICODE_STRING:
            self.loaded_data = entries.UnicodeString(self.data, 'Drive label')
        elif self.entry_type is EntryType.PROPERTY and self.value_type is EntryValueType.UNICODE_STRING:
            self.loaded_data = entries.UnicodeString(self.data)
        elif self.value_type is EntryValueType.AES_CCM_ENCRYPTED_KEY:
            self.loaded_data = entries.AesCcmEncryptedKey(self.data)
        elif self.value_type is EntryValueType.KEY:
            self.loaded_data = entries.Key(self.data)
        elif self.entry_type is EntryType.VMK and self.value_type is EntryValueType.VOLUME_MASTER_KEY:
            self.loaded_data = entries.VolumeMasterKey(self.data)
            current_offset = 28
            while current_offset < len(self.data):
                entry = self.load_from_data(self.data[current_offset:])
                self.loaded_data.properties.append(entry)
                current_offset += entry.size

    def __repr__(self):
        repr = f"""FveEntry:
    - size: 0x{self.size:08X}
    - entry type: 0x{self.entry_type.value:02X} {self.entry_type.name}
    - value type: 0x{self.value_type.value:02X} {self.value_type.name}
    - version: {self.version}"""
        if self.loaded_data is not None:
            repr += '\n'
            repr += ' ' * 4
            repr += '- Loaded data:'
            repr += '\n'
            repr += reindent(str(self.loaded_data), 8)
        else:
            repr += '\n'
            repr += ' ' * 4
            repr += f"- Raw data: {hexlify(self.data).decode('utf-8')}"
        return repr

    @classmethod
    def load_from_volume(cls, volume, offset):
        with open(volume, 'rb') as fp:
            fp.seek(offset)
            size = unpack("<H", fp.read(2))[0]
            entry_type = unpack("<H", fp.read(2))[0]
            value_type = unpack("<H", fp.read(2))[0]
            version = unpack("<H", fp.read(2))[0]
            data = fp.read(size - 8)
        with open(volume, 'rb') as fp:
            fp.seek(offset)
            raw_data = fp.read(size)
        return cls(size, entry_type, value_type, version, data, raw_data)
    
    @classmethod
    def load_from_data(cls, raw_data):
        size = unpack("<H", raw_data[:2])[0]
        entry_type = unpack("<H", raw_data[2:4])[0]
        value_type = unpack("<H", raw_data[4:6])[0]
        version = unpack("<H", raw_data[6:8])[0]
        data = raw_data[8:size]
        return cls(size, entry_type, value_type, version, data, raw_data)