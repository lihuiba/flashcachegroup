import FcgUtils
from FcgTable import FcgTable
class FcgCacheGroup(FcgTable):
    def __init__(self, name):
        FcgTable.__init__(self, name)

    def create(self, groupName, cacheDev, cacheSize):
        if self.is_existed():
            print '%s has been existed...' % self.name
            return False
        cmd = 'flashcache_create -p back -b 4k -s %s %s %s /dev/mapper/%s' % (cacheSize, self.name, cacheDev, groupName)
        try:
            FcgUtils.os_execute(cmd)
            return True
        except Exception, ErrMsg:
            print cmd + ': ' + ErrMsg
            return False

    def delete(self):
        ssdDev = self.get_cache_ssd_dev()
        ret = FcgTable.delete(self)
        if ret == False:
            return False
        cmd = 'flashcache_destroy -f %s' % ssdDev
        FcgUtils.os_execute(cmd)

    def get_cache_ssd_dev(self):
        cmd = "dmsetup table %s|grep ssd|grep dev|awk '{print $3}'" % self.name
        ssd_dev = FcgUtils.os_execute(cmd)[1:-2]
        return ssd_dev

    def get_cache_blksize(self):
        cmd = "dmsetup table %s |grep block|grep size|awk '{print $5}'" % self.name
        tmpSizeStr = FcgUtils.os_execute(cmd)
        blkSize = tmpSizeStr[tmpSizeStr.find('(')+1: tmpSizeStr.find(')')]
        return blkSize

    def invalid_cache_blocks(self, cacheGroupDev, startBlk, offsetBlk):
        cmd = 'flashcache_invalidate /dev/mapper/%s %s %s' % (self.name, startBlk, offsetBlk)
        FcgUtils.os_execute(cmd)
        
