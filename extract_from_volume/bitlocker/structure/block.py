"""
typedef struct _FVE_HEADER
{
	DWORD		size;
	DWORD		version;
	DWORD		header_size;
	DWORD		copy_size;
	GUID		volume_guid;
	DWORD		next_counter;
	WORD		algorithm;
	WORD		algorithm_unused;
	FILETIME	timestamp;
} FVE_HEADER, * PFVE_HEADER;
"""
import uuid
from typing import List
from datetime import datetime
from struct import pack,unpack
from binascii import hexlify, unhexlify

from .entry import FveEntry
from ..utils import reindent

class FveBlock:
    size: int = None
    version: int = None
    header_size: int = None
    copy_size: int = None
    volume_guid: uuid.UUID = None
    next_counter: int = None
    algorithm: int = None
    algorithm_unused: int = None
    timestamp: datetime = None
    entries: List[FveEntry] = []
    object_offset: int = 0

    def __init__(self, size, version, header_size, copy_size, volume_guid, next_counter, algorithm, algorithm_unused, timestamp, entries, object_offset=0):
        self.size = size
        self.version = version
        self.header_size = header_size
        self.copy_size = copy_size
        self.volume_guid = volume_guid
        self.next_counter = next_counter
        self.algorithm = algorithm
        self.algorithm_unused = algorithm_unused
        self.timestamp = timestamp
        self.object_offset = object_offset
        self.entries = entries
  
    def __repr__(self):
        repr = f"""FveBlock(0x{self.object_offset:04X}):
    - Size: {self.size}
    - Version: {self.version}
    - Header size: {self.header_size}
    - Copy size: {self.copy_size}
    - Volume guid: {self.volume_guid}
    - Next counter: 0x{self.next_counter:X} 
    - Algorithm: 0x{self.algorithm:X}
    - Timestamp: {self.timestamp}
    - Nb entries: {len(self.entries)}"""
        repr += "\n    Entries:"
        for entry in self.entries:
            repr += '\n'
            repr += reindent(str(entry), 8)
        return repr
        

    @classmethod
    def load_from_volume(cls, volume, block_offset):
        offset = block_offset + 0x40
        with open(volume, 'rb') as fp:
            fp.seek(offset)
            size = unpack("<I", fp.read(4))[0]
            version = unpack("<I", fp.read(4))[0]
            header_size = unpack("<I", fp.read(4))[0]
            copy_size = unpack("<I", fp.read(4))[0]
            volume_guid = uuid.UUID(bytes_le=fp.read(16))
            next_counter = unpack("<I", fp.read(4))[0]
            algorithm = unpack("<H", fp.read(2))[0]
            algorithm_unused = unpack("<H", fp.read(2))[0]
            timestamp = datetime.fromtimestamp(unpack("<Q", fp.read(8))[0]/ 10000000 - 11644473600)
        
        entries = [] 
        current_offset = offset + header_size
        while current_offset < offset + size:
            entry = FveEntry.load_from_volume(volume, current_offset)
            entries.append(entry)
            current_offset += entry.size

        return cls(size, version, header_size, copy_size, volume_guid, next_counter, algorithm, algorithm_unused, timestamp, entries, offset)
            

