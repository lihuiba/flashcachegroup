#!/usr/bin/env python
import sys, getopt
import FcgUtils
from FcgTable import FcgTable
from FcgCache import FcgCacheGroup
def parse_args(cmdline):
    try:
        opts, args = getopt.getopt(cmdline, "g:f", ["group=", "force"])
    except:
        sys.exit()

    groupName = ''
    force = False
    for a, o in opts:
        if a in ('-g', '--group'):
            groupName = o
        if a in ('-f', '--force'):
            force = True
    if groupName == '':
        sys.exit()
    return groupName, force

def delete_group(groupName, force=False):
    groupTable = FcgTable(groupName)
    if not groupTable.is_existed():
        print "Group % dose NOT exist..." % groupName
        return None

    hddDevices = []
    hddNames = []
    cachedDevices = []
    for line in groupTable.lines:
        if len(line) == 5:
            hddDevice = line['oriDev']
            hddDevices.append(hddDevice)
            hddName = hddDevice.split('/')[-1:][0]
            hddNames.append(hddName)
            cachedDevices.append('cache_' + hddName)

    if cachedDevices != [] and force == False:
        print "Delete group failed, Group %s is NOT empty..." % groupName
        return None

    freeTable = FcgTable('free_' + groupName)
    cacheName = 'cache_' + groupName
    cacheGroup = FcgCacheGroup('cache_' + groupName)

    freeTable.delete()
    for cachedDev in cachedDevices:
        cacheHddTable = FcgTable(cachedDev)
        cacheHddTable.delete()
    cacheGroup.delete()
    groupTable.delete()
    
if __name__ == '__main__':
    groupName, force = parse_args(sys.argv[1:])
    delete_group(groupName, force)
