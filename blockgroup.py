from struct import unpack_from

BlockGroupFields = [
    'block_bitmap', 'inode_bitmap', 'inode_table', 'free_blocks_count',
    'free_inodes_count', 'user_dirs_count', 'pad', 'reserved'
]

BlockGroupSize = 24

class BlockGroup():
    def __init__(self, data):
        unpacked = unpack_from('3I4HI', data)
        self.fields = dict(zip(BlockGroupFields, unpacked))
    def get_inode_table(self):
        return self.fields['inode_table']
