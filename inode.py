from struct import unpack, unpack_from

InodeFields = [
    'mode', 'uid', 'size', 'atime', 'ctime', 'mtime', 'dtime', 'gid',
    'links_count', 'blocks_count', 'flags', 'reserved1', 'blocks',
    'generation', 'file_acl', 'dir_acl', 'faddr', 'reserved2'
]

InodeSize = 128

class Inode():
    def __init__(self, data):
        unpacked = unpack_from('2H5I2H3I60s4I12s', data)
        self.fields = dict(zip(InodeFields, unpacked))
        self.blocks = list(unpack('15I', self.fields['blocks']))
    def __repr__(self):
        return repr(self.fields)
    def get_mode(self):
        return self.fields['mode']
    def get_uid(self):
        return self.fields['uid']
    def get_size(self):
        return self.fields['size']
    def get_atime(self):
        return self.fields['atime']
    def get_ctime(self):
        return self.fields['ctime']
    def get_mtime(self):
        return self.fields['mtime']
    def get_dtime(self):
        return self.fields['dtime']
    def get_gid(self):
        return self.fields['gid']
    def get_links_count(self):
        return self.fields['links_count']
    def get_blocks(self):
        return self.blocks[:11]
    def get_flags(self):
        return self.fields['flags']

    def is_directory(self):
        return (self.get_mode() & 0xF000) == 0x4000
    def is_file(self):
        return (self.get_mode() & 0xF000) == 0x8000
    def get_indirect_blocks(self, f, bs, level):
        if level == 1:
            block_addrs_pos = self.blocks[12] * bs
            f.seek(block_addrs_pos)
            data = f.read(bs)
            blocks = list(unpack('%dI' % (bs/4), data))
            return blocks
