"""
FVE_BLOCK_HEADER block_header = { 0 };
FVE_HEADER		 header = { 0 };
std::vector<std::shared_ptr<Buffer<PFVE_ENTRY>>> entries;

typedef struct _FVE_BLOCK_HEADER
{
    CHAR		signature[8]; 8
    WORD		size; 2
    WORD		version; 2
    WORD		curr_state; 2
    WORD		next_state; 2
    DWORD64		encrypted_volume_size; 8
    DWORD convert_size; 4
    DWORD nb_sectors; 4
    DWORD64		block_header_offsets[3]; 8*3 = 24
    DWORD64		backup_sector_offset; 8
} FVE_BLOCK_HEADER, * PFVE_BLOCK_HEADER;

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
from typing import List

from ..utils import *
from .block import FveBlock

class FveHeader:
    block: FveBlock = None

    def __init__(self, block):
        self.block = block
      
    @classmethod
    def load_from_volume(cls, volume, block_id=0):
        assert(block_id>=0 and block_id < 3)

        block_offset = get_fve_block_offset(volume)[block_id]

        block = FveBlock.load_from_volume(volume, block_offset)
            
        return  cls(block)

