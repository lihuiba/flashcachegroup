
from pydm.dmtable import LinearTable


class FcgLinearTable(LinearTable):
    def __init__(self, name, root_helper=''):
        super(FcgLinearTable, self).__init__(name, root_helper=root_helper)

    #TODO: initial here, Disk.from_error blabla....

    def exists(self, disk):
        for a_disk in self.disks[0:-1]:
            #print "in fcg.table disk.major_minor = %s, a_disk.major_minor = %s " % (disk.major_minor, a_disk.major_minor)
            if disk.major_minor == a_disk.major_minor:
                return True
        return False

    def insert_disk(self, new_disk):
        empty_disk = self.disks[-1]
        assert empty_disk.size > new_disk.size, 'NO sufficient space left'
        new_disk.start = empty_disk.start
        empty_disk.size -= new_disk.size
        empty_disk.start += new_disk.size
        self.disks.insert(-1, new_disk)
        self.reload_table()

    def remove_disk(self, the_disk):
        length = len(self.disks)
        for i in range(length):
            disk = self.disks[i]
            if disk.major_minor == the_disk.major_minor:
                disk.set_error()
                self.reload_table()
                return
        raise Exception("Could NOT find disk %s from table" % (the_disk.dev, self.name))

    @staticmethod
    def from_disks(name, disks, root_helper=''):
        linear_table = LinearTable.from_disks(name, disks, root_helper=root_helper, cls=FcgLinearTable)
        return linear_table