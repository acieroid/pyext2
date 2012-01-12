import fuse
from superblock import SuperBlock, SuperBlockSize
from blockgroup import BlockGroup, BlockGroupSize
from inode import Inode, InodeSize
from direntry import DirEntry, DirEntrySize

from stat import S_IFDIR

MaxBlocksRead = 10

class NotFound(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class Ext2(fuse.Fuse):
    def __init__(self, disk='foo.img', *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.disk = disk
        with open(self.disk, 'rb') as f:
            f.seek(1024)
            data = f.read(SuperBlockSize)
            self.sb = SuperBlock(data)
            first_group_pos = max(2048, self.sb.get_block_size())
            f.seek(first_group_pos)
            data = f.read(BlockGroupSize)
            self.first_bg = BlockGroup(data)
            root_i_pos = (self.sb.get_block_size() * 
                          self.first_bg.get_inode_table() + 
                          InodeSize)
            f.seek(root_i_pos)
            data = f.read(InodeSize)
            self.root_i = Inode(data)
    def find_inode(self, path):
        if path == '/':
            return self.root_i
        dirs = path.split('/')[1:]
        with open(self.disk, 'rb') as f:
            # TODO: deal with multiple-blocks directories
            next_de_pos = (self.root_i.get_blocks()[0] * 
                           self.sb.get_block_size())
            while dirs != []:
                f.seek(next_de_pos)
                data = f.read(DirEntrySize)
                de = DirEntry(data)
                if de.get_name_length() == 0:
                    raise NotFound("File %s not found" % path)
                if de.get_name() == dirs[0]:
                    dirs.pop()
                    inode_pos = (self.sb.get_block_size() * 
                                 self.first_bg.get_inode_table() +
                                 (de.get_inode()-1) * InodeSize)
                    f.seek(inode_pos)
                    data = f.read(InodeSize)
                    i = Inode(data)
                    if dirs == []: # we found it
                        return i
                    if i.is_file():
                        raise NotFound("%s is a file, not a directory" % 
                                       de.get_name())
                    # TODO
                    next_de_pos = (i.get_blocks()[0] *
                                   self.sb.get_block_size())
                next_de_pos += de.get_length()
        raise NotFound("Invalid path: %s" % path)

    def getattr(self, path):
        inode = self.find_inode(path)
        stat = fuse.Stat()
        stat.st_mode = inode.get_mode()
        stat.st_atime = inode.get_atime()
        stat.st_mtime = inode.get_mtime()
        stat.st_ctime = inode.get_ctime()
        stat.st_uid = inode.get_uid()
        stat.st_gid = inode.get_gid()
        stat.st_size = inode.get_size()
        stat.st_nlink = inode.get_links_count()
        stat.st_ino = 0 # TODO
        stat.st_dev = 0

        return stat

    def readdir(self, path, offset):
        inode = self.find_inode(path)
        with open(self.disk, 'rb') as f:
            next_de_pos = (inode.get_blocks()[0] *
                           self.sb.get_block_size())
            while True:
                f.seek(next_de_pos)
                data = f.read(DirEntrySize)
                de = DirEntry(data)
                if de.get_name_length() == 0:
                    break
                yield fuse.Direntry(de.get_name())
                next_de_pos += de.get_length()
        return
    def mknod(self, path, mode, dev):
        return 0
  
    def unlink(self, path):
        return 0
  
    def read(self, path, size, offset):
        blocks_read = 0
        inode = self.find_inode(path)
        first_block = offset/self.sb.get_block_size()
        data = ''
        with open(self.disk, 'rb') as f:
            all_blocks = (inode.get_blocks() +
                          inode.get_indirect_blocks(f, self.sb.get_block_size(), 1))
            for block in all_blocks[first_block:]:
                if block != 0:
                    blocks_read += 1
                    if blocks_read >= MaxBlocksRead:
                        # we can't give too much data at once
                        return data
                    block_pos = (block * self.sb.get_block_size())
                    f.seek(block_pos)
                    data += f.read(self.sb.get_block_size())
        return data

    def write(self, path, buf, offset):
        return 0
  
    def release(self, path, flags):
        return 0
  
    def open(self, path, flags):
        return 0
  
    def truncate(self, path, size):
        return 0
  
    def utime(self, path, times):
        return 0
  
    def mkdir(self, path, mode):
        return 0
  
    def rmdir(self, path):
        return 0
  
    def rename(self, pathfrom, pathto):
        return 0
  
    def fsync(self, path, isfsyncfile):
        return 0

if __name__ == '__main__':
    fuse.fuse_python_api = (0, 2)
    server = Ext2(disk='foo.img',
                  usage=fuse.Fuse.fusage,
                  version=fuse.__version__)
    server.parse()
    server.main()
