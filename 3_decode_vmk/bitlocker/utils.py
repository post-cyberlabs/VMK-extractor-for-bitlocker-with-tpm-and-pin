from struct import pack,unpack

# From https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s12.html
def reindent(s: str, numSpaces):
    s = s.split('\n')
    s = [(numSpaces * ' ') + line for line in s]
    s = '\n'.join(s)
    return s

def is_bitlocker_volume(volume):
    with open(volume, 'rb') as fp:
        fp.seek(3)
        oemID = fp.read(8)
        if oemID == b'-FVE-FS-':
            return True
    return False

def read_fve_block():
    """
    FVE_BLOCK_HEADER block_header = { 0 };
	FVE_HEADER		 header = { 0 };
	std::vector<std::shared_ptr<Buffer<PFVE_ENTRY>>> entries;
    """
    pass

def get_fve_block_offset(volume):
    with open(volume, 'rb') as fp:
        fp.seek(0xb0)
        block1 = unpack("<Q", fp.read(8))[0]
        block2 = unpack("<Q", fp.read(8))[0]
        block3 = unpack("<Q", fp.read(8))[0]

    return block1, block2, block3