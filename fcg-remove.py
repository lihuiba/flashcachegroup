#!/usr/bin/env python
import sys, getopt
import FcgUtils

def parse_args(cmdline):
    try:
        opts, args = getopt.getopt(cmdline, "g:h:", ["group=", "hdddev="])
    except Exception, e:
        sys.exit()
    groupName = ''
    hddDev = ''
    for a, o in opts:
        if a in ('-g', '--group'):
            groupName = o
        if a in ('-h', '--hdddev'):
            hddDev = o
    if groupName == '' or hddDev == '':
        sys.exit()
    return groupName, hddDev

def delete_hdd(groupName, hddDev):
    hddName = hddDev.split('/')[-1:][0]
    cacheHddName = 'cache_' + hddName
    cmd = 'dmsetup table %s' % cacheHddName
    cacheHddTable =  FcgUtils.os_execue(cmd)
    startSec, offset, type, oriDev, oriStartSec = cacheHddTable.split()
    startSec, offset, oriStartSec = map(int, [startSec, offset, oriStartSec])
    #delete cache_hdd table 
    FcgUtils.delete_table(cacheHddName) 
    cacheTableName = 'cache_%s' % groupName
    cacheBlkSize = FcgUtils.get_cache_blksize(cacheTableName)
    startBlk, offsetBlk = FcgUtils.sector_offset2block_offset(oriStartSec, offset, cacheBlkSize)
    FcgUtils.invalid_cache_blocks(cacheTableName, startBlk, offsetBlk)
    #reload group table
    cmd = 'dmsetup table %s' % groupName
    groupTable = FcgUtils.os_execue(cmd)
    newGroupTable = ''
    found = False
    newStartGroupSec = 0
    newOffsetGroup = 0
    groupTabList = groupTable.split('\n')
    for groupLine in groupTabList:
        groupLine = groupLine.split()
        if len(groupLine) == 5:
            startGroupSec, offsetGroup, typeGroup, oriGroupDev, oriGroupStartSec = groupLine
            startGroupSec, offsetGroup, oriGroupStartSec = map(int, [startGroupSec, offsetGroup, oriGroupStartSec])
            oriGroupDev = FcgUtils.get_devname_from_major_minor(oriGroupDev)
            if offsetGroup == offset and oriGroupDev == hddDev:
                newStartGroupSec = startGroupSec
                newOffsetGroup = offsetGroup
                found = True
                newGroupTable += ' '.join([str(newStartGroupSec), str(newOffsetGroup), 'error'])
                newGroupTable += '\n'
            else:
                newGroupTable += ' '.join(groupLine)
                newGroupTable += '\n'
        elif len(groupLine) == 3:
                newGroupTable += ' '.join(groupLine)
                newGroupTable += '\n'
    if not found:
        print 'Could NOT find %s in group %s' % (hddDev, groupName)
        return
    preSec = 0
    preOffset = 0
    preType = ''
    reComputeGroupTable = ''
    newFreeTable = ''
    newFreeStartSec = 0
    cacheDevice = '/dev/mapper/cache_%s' % groupName
    for newGroupLine in newGroupTable.split('\n'):
        newGroupLine = newGroupLine.split()
        if len(newGroupLine) == 3:
            startGroupSec, offsetGroup, typeGroup = newGroupLine
            startGroupSec, offsetGroup = map(int, [startGroupSec, offsetGroup])
            assert typeGroup == 'error', 'something WRONG in group table'
            if preType == 'error':
                preOffset += offsetGroup
            else:
                preSec, preOffset, preType = [startGroupSec, offsetGroup, typeGroup]
        elif len(newGroupLine) == 5:
            startGroupSec, offsetGroup, typeGroup, oriGroupDev, oriGroupStartSec = newGroupLine
            startGroupSec, offsetGroup, oriGroupStartSec = map(int, [startGroupSec, offsetGroup, oriGroupStartSec])
            if preType == 'error':
                reComputeGroupTable += ' '.join([str(preSec), str(preOffset), preType])
                reComputeGroupTable += '\n'
                newFreeTable += ' '.join([str(newFreeStartSec), str(preOffset), 'linear', cacheDevice, str(preSec)])
                newFreeTable += '\n'
                newFreeStartSec += preOffset
            preSec, preOffset, preType = [startGroupSec, offsetGroup, typeGroup]
            reComputeGroupTable += ' '.join(newGroupLine)
            reComputeGroupTable += '\n'
    if preType == 'error':
        reComputeGroupTable += ' '.join([str(preSec), str(preOffset), preType])
        reComputeGroupTable += '\n'
        newFreeTable += ' '.join([str(newFreeStartSec), str(preOffset), 'linear', cacheDevice, str(preSec)])
        newFreeTable += '\n'
        newFreeStartSec += preOffset
    freeName = 'free_%s' % groupName
    FcgUtils.reload_table(groupName, reComputeGroupTable)
    FcgUtils.reload_table(freeName, newFreeTable)

if __name__ == '__main__':
    groupName, hddDev = parse_args(sys.argv[1:])
    delete_hdd(groupName, hddDev)
