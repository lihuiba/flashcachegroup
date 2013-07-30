#!/usr/bin/env python
import commands, tempfile

def bytes_str2bytes_count(bytes):
    #take M as default
    bytes_num = 0
    if bytes.endswith('P') or bytes.endswith('p'):
        bytes_num = int(bytes[:-1])*1024*1024*1024*1024*1024
    elif bytes.endswith('T') or bytes.endswith('t'):
        bytes_num = int(bytes[:-1])*1024*1024*1024*1024
    elif bytes.endswith('G') or bytes.endswith('g'):
        bytes_num = int(bytes[:-1])*1024*1024*1024
    elif bytes.endswith('M') or bytes.endswith('m'):
        bytes_num = int(bytes[:-1])*1024*1024
    elif bytes.endswith('K') or bytes.endswith('k'):
        bytes_num = int(bytes[:-1])*1024
    else:
        bytes_num = int(bytes)*1024*1024
    return bytes_num

def bytes2sectors(bytes):
    bytes = bytes_str2bytes_count(bytes)
    sectors = bytes/512
    return sectors

def sector_offset2block_offset(startSector, offset, blkSize):
    blkSize = bytes_str2bytes_count(blkSize)
    startBlk = startSector * 512 / blkSize
    offsetBlk = offset * 512 / blkSize
    return startBlk, offsetBlk

def sectors2MB(sectors):
    return str(sectors*512/1024/1024) + 'M'

def os_execute(cmd):
    ret, output = commands.getstatusoutput(cmd)
    if ret == '0' or ret == 0:
        return output
    else:
        raise Exception(output)

def write2tempfile(content):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    temp.close()
    return temp.name


def get_devname_from_major_minor(majorMinor):
    # try os.readlink('/dev/block/<major>:<minor>')
    cmd = "ls -l /dev/block|awk '{print $9, $11}'|grep %s" % majorMinor
    _, deviceName = os_execute(cmd).split()
    deviceName = deviceName.split('/')[-1:][0]
    if majorMinor.split(':')[0] == '253':
        cmd = "ls -l /dev/mapper|awk '{if ($11 != \"\") print $11, $9}'|grep %s"% deviceName
        _, deviceName = os_execute(cmd).split()
        return '/dev/mapper/%s' % deviceName   
    else:
        return '/dev/%s' % deviceName

def get_dev_sector_count(dev):
    # try /dev/block/xxx/size
    cmd = 'blockdev --getsz %s'%dev
    devSector = os_execute(cmd)
    if type(devSector) != int:
        try:
            devSector = int(devSector)
        except:
            return 0
    return devSector

def get_free_table_from_group(groupStruct, cacheGroupDev):
    startSec = 0
    freeTable = []
    for line in groupStruct:
        if len(line) == 3:
            offset = line['offset']
            oriStartSec = line['startSec']
            tempDict = {'startSec':startSec, 'offset':offset, 'type':'linear', 'oriDev':cacheGroupDev, 'oriStartSec':oriStartSec}
            freeTable.append(tempDict)
            startSec += offset
    return freeTable
                
def test_get_devname_from_major_minor():
    for mm in ['7:2', '253:5']:
        print get_devname_from_major_minor(mm)
def test_get_cache_ssd_dev():
    print get_cache_ssd_dev('cache_testgroup')
def test_get_cache_blksize():
    print get_cache_blksize('cache_testgroup')

if __name__ == '__main__':
    pass
