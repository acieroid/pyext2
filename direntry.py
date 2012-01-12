from struct import unpack_from

DirEntryFields = [
    'inode', 'rec_len', 'name_len', 'file_type', 'name'
]

DirEntrySize = 263

class DirEntry():
    def __init__(self, data):
        unpacked = unpack_from('IH2b255s', data)
        self.fields = dict(zip(DirEntryFields, unpacked))
    def get_inode(self):
        return self.fields['inode']
    def get_length(self):
        return self.fields['rec_len']
    def get_name_length(self):
        return self.fields['name_len']
    def get_name(self):
        return self.fields['name'][:self.get_name_length()]
