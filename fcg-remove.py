#!/usr/bin/env python
import sys, getopt
import FcgUtils
from FcgTable import FcgTable
from FcgCache import FcgCacheGroup

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

def remove_hdd(groupName, hddDev):
    groupTable = FcgTable(groupName)
    if not groupTable.is_existed():
        print 'Group %s does NOT exist...' % groupName
        return False

    cacheHddTable = FcgTable('cache_' + hddDev.split('/')[-1:][0])
    if not cacheHddTable.is_existed():
        print 'hdd %s does NOT exist in group %s...' % (hddDev, groupName)
        return False

    assert len(cacheHddTable.lines) == 1, 'Multi line found in table of %s' % cacheHddTable.name
    cacheLine = cacheHddTable.lines[0]
    assert len(cacheLine) == 5, 'Could NOT support table format for %s' % (cacheHddTable.name)
    cacheHddTable.delete()

    #invalid cache blocks
    cacheGroupName = 'cache_%s' % groupName
    cacheGroupDev = '/dev/mapper/%s' % cacheGroupName
    cacheGroup = FcgCacheGroup(cacheGroupName)
    cacheBlkSize = cacheGroup.get_cache_blksize()
    startBlk, offsetBlk = FcgUtils.sector_offset2block_offset(cacheLine['oriStartSec'], cacheLine['offset'], cacheBlkSize)
    cacheGroup.invalid_cache_blocks(cacheGroupDev, startBlk, offsetBlk)
    
    for i in range(len(groupTable.lines)):
        groupLine = groupTable.lines[i]
        if len(groupLine) == 5:
            if groupLine['offset'] == cacheLine['offset'] and groupLine['oriDev'] == hddDev:
                groupTable.lines[i] = {'startSec':groupLine['startSec'], 'offset':groupLine['offset'], 'type':'error'}
                break
    groupTable.reload()
    freeTable = FcgTable('free_'+groupName)
    freeTable.lines = FcgUtils.get_free_table_from_group(groupTable.lines, cacheGroupDev)
    freeTable.reload()

if __name__ == '__main__':
    groupName, hddDev = parse_args(sys.argv[1:])
    remove_hdd(groupName, hddDev)
