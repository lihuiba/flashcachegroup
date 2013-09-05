#!/usr/bin/env python
import sys, os
import FcgUtils

def add_hdd(groupName, hddDev):
    groupTable = FcgTable(groupName)
    if not groupTable.is_existed():
        print 'Group %s does NOT exist...' % groupName
        return False
        
    cacheTable = FcgTable('cache_' + hddDev.split('/')[-1:][0])
    if cacheTable.is_existed():
        print 'Hdd %s has already been existed in the group...'%hddDev
        return False

    if not os.path.exists(hddDev):
        print 'Hdd %s does NOT exist at all...' % hddDev
        return False

    devSectorCount = FcgUtils.get_dev_sector_count(hddDev)
    if devSectorCount <= 0:
        print 'Hdd %s should NOT be empty...' % hddDev
        return False
 
    startSec = -1
    offset = -1
    for i in range(len(groupTable.lines)):
        line = groupTable.lines[i]
        if line['type'] == 'error' and line['offset'] >= devSectorCount:
            startSec = line['startSec']
            offset = line['offset']
            newHddLine = {'startSec':startSec, 'offset':devSectorCount, 'type':'linear', 'oriDev':hddDev, 'oriStartSec':0}
            
            if line['offset'] > devSectorCount:
                line['startSec'] += devSectorCount
                line['offset'] -= devSectorCount
                groupTable.lines.insert(i, newHddLine)
            else: #line['offset'] == devSectorCount:
                groupTable.lines[i] = newHddLine
            break
    freeTable = FcgTable('free_'+groupName)
    cacheGroupName = 'cache_%s' % groupName
    cacheGroupDev = '/dev/mapper/%s' % cacheGroupName
    freeTable.lines = FcgUtils.get_free_table_from_group(groupTable.lines, cacheGroupDev)

    cacheTableContent = ' '.join(['0', str(devSectorCount), 'linear', cacheGroupDev, str(startSec)])
    cacheTable.set_lines(cacheTableContent)

    groupTable.reload()
    freeTable.reload()
    cacheTable.create()

