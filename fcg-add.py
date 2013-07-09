#!/usr/bin/env python
import sys, getopt
import FcgUtils
from FcgTable import FcgTable

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

def add_hdd(groupName, hddDev):
    cacheTable = FcgTable('cache_' + hddDev.split('/')[-1:][0])
    if cacheTable.is_existed():
        print 'Hdd %s has already been existed...'%hddDev
        return False

    devSectorCount = FcgUtils.get_dev_sector_count(hddDev)
    groupTable = FcgTable(groupName)
    startSec = -1
    offset = -1
    for i in range(len(groupTable.lines)):
        line = groupTable.lines[i]
        if line['type'] == 'error' and line['offset'] >= devSectorCount:
            startSec = line['startSec']
            offset = line['offset']
            newHddLine = {'startSec':startSec, 'offset':devSectorCount, 'type':'linear', 'oriDev':hddDev, 'oriStartSec':0}
            
            groupTable.lines.remove(line)
            groupTable.lines.insert(i, newHddLine)
            if line['offset'] > devSectorCount:
                newErrLine = {'startSec':startSec+devSectorCount, 'offset':offset-devSectorCount, 'type':'error'}
                groupTable.lines.insert(i+1,newErrLine)
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

if __name__ == '__main__':
    groupName, hddDev = parse_args(sys.argv[1:])
    add_hdd(groupName, hddDev)
