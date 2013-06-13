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

def add_hdd(groupName, hddDev):
    devSectorCount = FcgUtils.get_dev_sector_count(hddDev)
    cmd = 'dmsetup table %s' % groupName
    dmTable = FcgUtils.os_execue(cmd)
    newTable = ''
    hasInserted = False
    insertedStartSector = 0
    insertedOffset = devSectorCount
    for tableLine in dmTable.split('\n'):
        if tableLine.find('error') != -1 and hasInserted == False:
            startSector, offset, error = tableLine.split()
            startSector, offset = map(int, [startSector, offset])
            if offset >= devSectorCount:
                insertedStartSector = startSector
                newTable += ' '.join([str(startSector), str(devSectorCount), 'linear', hddDev, '0'])
                newTable += '\n'
                hasInserted = True
                offset -= devSectorCount
                if offset > 0:
                    newTable += ' '.join([str(startSector+devSectorCount), str(offset-devSectorCount), 'error'])
                    newTable += '\n'
        else:
            newTable += tableLine
            newTable += '\n'
    if hasInserted:
        FcgUtils.reload_table(groupName, newTable)

        freeName = 'free_'+groupName
        cmd = 'dmsetup table %s' % freeName
        freeTable = FcgUtils.os_execue(cmd)
        newFreeTable = ''
        newHddTable = ''
        hasInsertedFree = False
        newFreeStartSec = 0
        for freeLine in freeTable.split('\n'):
            startSector, offset, type, device, deviceStartSector = freeLine.split()
            startSector, offset, deviceStartSector = map(int, [startSector, offset, deviceStartSector])
            if deviceStartSector == insertedStartSector:
                assert offset >= insertedOffset, 'Create cache device for HDD failed...'
                newHddTable = ' '.join(['0', str(insertedOffset), 'linear', device, str(insertedStartSector)])
                if offset-insertedOffset > 0:
                    newFreeTable += ' '.join([str(newFreeStartSec), str(offset-insertedOffset), 'linear', device, str(deviceStartSector+insertedOffset)])+'\n'
                    newFreeStartSec += (offset-insertedOffset)
            else:
                newFreeTable += ' '.join([str(newFreeStartSec), str(offset), 'linear', device, str(deviceStartSector)])+'\n'
        cacheHddName = 'cache_' + hddDev.split('/')[-1:][0]
        #print newFreeTable
        #print newHddTable
        FcgUtils.reload_table(freeName, newFreeTable)
        FcgUtils.create_table(cacheHddName, newHddTable)
if __name__ == '__main__':
    groupName, hddDev = parse_args(sys.argv[1:])
    add_hdd(groupName, hddDev)
