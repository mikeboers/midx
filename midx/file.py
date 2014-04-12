import collections


class File(object):

    def __init__(self, id, sequence, number, inode, device, size, mtime, ctime, itime=None, checksum=None):
        self.id = id
        self.sequence = sequence
        self.number = number
        self.inode = inode
        self.device = device
        self.size = size
        self.mtime = mtime
        self.ctime = ctime
        self.itime = itime
        self.checksum = checksum
