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
            newErrLine = {'startSec':startSec+devSectorCount, 'offset':offset-devSectorCount, 'type':'error'}
            groupTable.lines.remove(line)
            groupTable.lines.insert(i, newHddLine)
            groupTable.lines.insert(i+1,newErrLine)
            break
    freeTable = FcgTable('free_'+groupName)
    newFreeStartSec = 0
    newLines = []
    cacheHddTableContent = ''
    for line in freeTable.lines:
        #line = freeTable.lines[i]
        if line['oriStartSec'] == startSec:
            assert line['offset'] >= devSectorCount, 'Create cache device for HDD failed...'
            newFreeLine = {'startSec':newFreeStartSec, 'offset':line['offset']-devSectorCount, 'type':'linear', 'oriDev':line['oriDev'], 'oriStartSec':line['oriStartSec']+devSectorCount}
            newLines.append(newFreeLine)
            cacheHddTableContent = ' '.join(['0', str(devSectorCount), 'linear', line['oriDev'], str(startSec)])
            newFreeStartSec += line['offset']-devSectorCount
        else:
            newFreeLine = {'startSec':newFreeStartSec, 'offset':line['offset'], 'type':'linear', 'oriDev':line['oriDev'], 'oriStartSec':line['oriStartSec']}
            newFreeStartSec += line['offset']
            newLines.append(newFreeLine)
    freeTable.lines = newLines
    cacheTable = FcgTable('cache_' + hddDev.split('/')[-1:][0])
    cacheTable.set_lines(cacheHddTableContent)
    print groupTable.lines
    print freeTable.lines
    print cacheTable.lines
    groupTable.reload()
    freeTable.reload()
    cacheTable.create()

if __name__ == '__main__':
    groupName, hddDev = parse_args(sys.argv[1:])
    add_hdd(groupName, hddDev)
