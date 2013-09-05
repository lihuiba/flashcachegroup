#!/usr/bin/env python
import sys
import FcgUtils
from FcgTable import FcgTable
from FcgCache import FcgCacheGroup

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
