#!/usr/bin/env python
import sys, getopt
import FcgUtils

def parse_args(cmdline):
    try:
        opts, args = getopt.getopt(cmdline, "g:h:c:c:", ["group=", "hddsize=", "cachedev=", "cachesize="])
    except Exception, e:
        sys.exit()

    groupName = ''
    hddSize = ''
    cacheDev = ''
    cacheSize = ''
    for a, o in opts:
        if a in ('-g', '--group'):
            groupName = o
        if a in ('-hs', '--hddsize'):
            hddSize = o
        if a in ('-cd', '--cachedev'):
            cacheDev = o
        if a in ('-cs', '--cachesize'):
            cacheSize = o
    if groupName == '' or hddSize == '' or cacheDev == '' or cacheSize == '':
        sys.exit()
    return groupName, hddSize, cacheDev, cacheSize

def create_group(groupName, hddSize, cacheDev, cacheSize):
    hddSectors = FcgUtils.bytes2sectors(hddSize)
    dmTable = '0 %s error\n' % hddSectors
    FcgUtils.create_table(groupName, dmTable)
    cacheName = 'cache_' + groupName
    cmd = 'flashcache_create -p back -b 4k -s %s %s %s /dev/mapper/%s' % (cacheSize, cacheName, cacheDev, groupName)
    FcgUtils.os_execue(cmd)

    freeTable = '0 %s linear /dev/mapper/%s 0\n'%(hddSectors, cacheName)
    freeName = 'free_'+groupName
    FcgUtils.create_table(freeName, freeTable)

if __name__ == '__main__':
    groupName, hddSize, cacheDev, cacheSize = parse_args(sys.argv[1:])
    create_group(groupName, hddSize, cacheDev, cacheSize)

