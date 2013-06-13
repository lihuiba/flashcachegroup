#!/usr/bin/env python
import sys, getopt
import FcgUtils

def parse_args(cmdline):
    try:
        opts, args = getopt.getopt(cmdline, "g:", ["group="])
    except:
        sys.exit()

    groupName = ''
    for a, o in opts:
        if a in ('-g', '--group'):
            groupName = o
    if groupName == '':
        sys.exit()
    return groupName

def delete_group(groupName):
    cmd = 'dmsetup table %s' % groupName
    groupTable =  FcgUtils.os_execue(cmd)
    hddDevices = []
    hddNames = []
    cachedDevices = []
    for groupLine in groupTable.split('\n'):
        groupLine = groupLine.split()
        if len(groupLine) == 5:
            hddMajorMinor = groupLine[3]
            hddDevice = FcgUtils.get_devname_from_major_minor(hddMajorMinor)
            hddDevices.append(hddDevice)
            hddName = hddDevice.split('/')[-1:][0]
            hddNames.append(hddName)
            cachedDevices.append('cache_' + hddName)
    freeTableName = 'free_' + groupName
    cacheTableName = 'cache_' + groupName

    ssdDev = FcgUtils.get_cache_ssd_dev(cacheTableName)

    FcgUtils.delete_table(freeTableName)
    for cachedDev in cachedDevices:
        FcgUtils.delete_table(cachedDev)
    FcgUtils.delete_table(cacheTableName)
    FcgUtils.delete_table(groupName)
    
    cmd = 'flashcache_destroy -f %s' % ssdDev
    FcgUtils.os_execue(cmd)

if __name__ == '__main__':
    groupName = parse_args(sys.argv[1:])
    delete_group(groupName)
