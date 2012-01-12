from struct import unpack_from
from uuid import UUID

SuperBlockFields = [
    'inodes_count', 'blocks_count', 'r_blocks_count', 'free_blocks_count',
    'free_inodes_count', 'first_data_block', 'log_block_size', 'log_frag_size',
    'blocks_per_group','frags_per_group', 'inodes_per_group', 'mtime', 'wtime',
    'mnt_count', 'max_mnt_count', 'magic', 'state', 'errors', 'minor_rev_level',
    'lastcheck', 'checkinterval', 'creator_os', 'rev_level', 'def_resuid',
    'def_resgid', 'first_ino', 'inode_size', 'block_group_nr', 'feature_compat',
    'feature_incompat', 'feature_ro_compat', 'uuid', 'volume_name',
    'last_mounted', 'algorithm_usage_bitmap', 'prealloc_blocks',
    'prealloc_dir_blocks', 'padding1', 'journal_uuid', 'journal_inum',
    'journal_dev', 'last_orphan', 'hash_seed', 'def_hash_version',
    'reserved_char_pad', 'reserved_word_pad', 'default_mount_opts',
    'first_meta_bg', 'reserved'
]

SuperBlockSize = 1024

def if_null(string, alternative):
    if len(string) > 0 and string[0] == '\0':
        return alternative
    else:
        return string

class SuperBlock():
    def __init__(self, data):
        unpacked = unpack_from('13I6H4I2HI2H3I16s16s64sIccH16s3I16sccH2I760s',
                          data)
        self.fields = dict(zip(SuperBlockFields, unpacked))
    def get_volume_name(self):
        return if_null(self.fields['volume_name'], '')
    def get_last_mountpoint(self):
        return if_null(self.fields['last_mounted'], '')
    def get_uuid(self):
        return UUID(bytes=self.fields['uuid'])
    def get_magic_number(self):
        return self.fields['magic']
    def get_creator_os(self):
        oses = ['Linux', 'Hurd', 'Masix', 'FreeBSD', 'Lites']
        if self.fields['creator_os'] in xrange(len(oses)):
            return oses[self.fields['creator_os']]
    def get_inodes_count(self):
        return self.fields['inodes_count']
    def get_blocks_count(self):
        return self.fields['blocks_count']
    def get_block_size(self):
        return (1024 << self.fields['log_block_size'])
    def get_fragment_size(self):
        return (1024 << self.fields['log_frag_size'])
    def get_inode_size(self):
        return self.fields['inode_size']
    def get_blocks_per_group(self):
        return self.fields['blocks_per_group']
    def get_fragments_per_group(self):
        return self.fields['frags_per_group']
    def get_inodes_per_group(self):
        return self.fields['inodes_per_group']
