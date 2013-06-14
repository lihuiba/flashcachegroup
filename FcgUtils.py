#!/usr/bin/env python
import commands, tempfile

def sectors2Mb(sectors):
    return str(sectors*512/1024/1024) + 'M'

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

#should be 'MB'
def sectors2Mb(sectors):
    return str(sectors*512/1024/1024) + 'M'

def os_execue(cmd):
    try:
        ret, output = commands.getstatusoutput(cmd)
        if ret == '0' or ret == 0:
            return output
        else:
            raise 'Execute %s failed...'%cmd
    except Exception, e:
        print e
        print 'Execute %s failed!' % cmd
        return None

def write2tempfile(content):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    temp.close()
    return temp.name


def get_devname_from_major_minor(majorMinor):
    # try os.readlink('/dev/block/<major>:<minor>')
    cmd = "ls -l /dev/block|awk '{print $9, $11}'|grep %s" % majorMinor
    _, deviceName = os_execue(cmd).split()
    deviceName = deviceName.split('/')[-1:][0]
    if majorMinor.split(':')[0] == '253':
        cmd = "ls -l /dev/mapper|awk '{if ($11 != \"\") print $11, $9}'|grep %s"% deviceName
        _, deviceName = os_execue(cmd).split()
        return '/dev/mapper/%s' % deviceName   
    else:
        return '/dev/%s' % deviceName

def get_dev_sector_count(dev):
    # try /dev/block/xxx/size
    cmd = 'blockdev --getsz %s'%dev
    devSector = os_execue(cmd)
    if type(devSector) != int:
        devSector = int(devSector)
    return devSector

def create_table(tableName, tableContent):
    tmpTableFile = write2tempfile(tableContent) 
    cmd = 'dmsetup create %s %s' % (tableName, tmpTableFile)
    # try using pipe instead of temp file via os.subprocess
    os_execue(cmd)

def reload_table(tableName, tableContent):
    cmd = 'dmsetup suspend %s'%tableName
    os_execue(cmd)
    tmpTableFile = write2tempfile(tableContent)
    cmd = 'dmsetup reload %s %s' % (tableName, tmpTableFile)
    os_execue(cmd)
    cmd = 'dmsetup resume %s'%tableName
    os_execue(cmd)

def delete_table(tableName):
    cmd = 'dmsetup remove %s'%tableName
    os_execue(cmd)

def get_table_str(tableName):
    cmd = 'dmsetup table %s' % tableName
    tableContent = os_execue(cmd)
    assert tableContent != '', 'Could NOT find %s in dm table' % tableName
    return tableContent

def get_table_struct_from_str(tableStr):
    tableStruct = []
    tableList = tableStr.split('\n')
    for tableLine in tableList:
        tableLineList = tableLine.split()
        tempDict = {}
        if len(tableLineList) == 5:
            startSec, offset, type, oriDev, oriStartSec = tableLineList
            oriDev = get_devname_from_major_minor(oriDev)
            startSec, offset, oriStartSec = map(int, [startSec, offset, oriStartSec])
            tempDict = {'startSec':startSec, 'offset':offset, 'type':type, 'oriDev':oriDev, 'oriStartSec':oriStartSec}
        elif len(tableLineList) == 3:
            startSec, offset, type = tableLineList
            startSec, offset = map(int, [startSec, offset])
            tempDict = {'startSec':startSec, 'offset':offset, 'type':type}
        else:
            print 'Could NOT support table format %s' % tableLine

        if len(tempDict) != 0:
            tableStruct.append(tempDict)
    return tableStruct

def get_table_str_from_struct(tableStruct):
    tableStr = ''
    for line in tableStruct:
        if len(line) == 5:
            tableStr += ' '.join([str(line['startSec']), str(line['offset']), line['type'], line['oriDev'], str(line['oriStartSec'])]) + '\n'
        elif len(line) == 3:
            tableStr += ' '.join([str(line['startSec']), str(line['offset']), line['type']]) + '\n'
    return tableStr
            
def adjust_table_struct(tableStruct):
    '''Merge adjacent error line in table struct '''
    adjustTable = []
    preSec = 0
    preOffset = 0
    preType = ''
    for line in tableStruct:
        if len(line) == 3:
            startSec, offset, type = [line['startSec'], line['offset'], line['type']]
            assert line['type'] == 'error', 'something WRONG in group table'
            if preType == 'error':
                preOffset += offset
            else:
                preSec, preOffset, preType = [startSec, offset, type]
        elif len(line) == 5:
            startSec, offset, type, oriDev, oriStartSec = [line['startSec'], line['offset'], line['type'], line['oriDev'], line['oriStartSec']]
            if preType == 'error':
                tempDict = {'startSec':preSec, 'offset':preOffset, 'type':preType}
                adjustTable.append(tempDict)
            adjustTable.append(line)
            preSec, preOffset, preType = [startSec, offset, type]
    if preType == 'error':
        tempDict = {'startSec':preSec, 'offset':preOffset, 'type':preType}
        adjustTable.append(tempDict)
    return adjustTable

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
                
def get_cache_ssd_dev(cacheTableName):
    cmd = "dmsetup table %s|grep ssd|grep dev|awk '{print $3}'" % cacheTableName
    ssd_dev = os_execue(cmd)[1:-2]
    return ssd_dev

def get_cache_blksize(cacheTableName):
    cmd = "dmsetup table %s |grep block|grep size|awk '{print $5}'" % cacheTableName
    tmpSizeStr = os_execue(cmd)
    blkSize = tmpSizeStr[tmpSizeStr.find('(')+1: tmpSizeStr.find(')')]
    return blkSize

def invalid_cache_blocks(cacheGroupDev, startBlk, offsetBlk):
    cmd = 'flashcache_invalidate %s %s %s' % (cacheGroupDev, startBlk, offsetBlk)
    os_execue(cmd)

def test_get_devname_from_major_minor():
    for mm in ['7:2', '253:5']:
        print get_devname_from_major_minor(mm)
def test_get_cache_ssd_dev():
    print get_cache_ssd_dev('cache_testgroup')
def test_get_cache_blksize():
    print get_cache_blksize('cache_testgroup')

if __name__ == '__main__':
    test_get_cache_blksize()
