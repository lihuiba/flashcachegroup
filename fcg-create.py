#!/usr/bin/env python
import sys, getopt
import FcgUtils

def parse_args(cmdline):
    try:
        opts, args = getopt.getopt(cmdline, "g:c:", ["group=", "cachedev="])
    except Exception, e:
        sys.exit()

    groupName = ''
    cacheDev = ''
    for a, o in opts:
        if a in ('-g', '--group'):
            groupName = o
        if a in ('-c', '--cachedev'):
            cacheDev = o
    if groupName == '' or cacheDev == '':
        sys.exit()
    return groupName, cacheDev

def __create_group(groupName, cacheDev, hddSize, cacheSize):
    hddSectors = str(FcgUtils.bytes2sectors(hddSize))
    dmTable = '0 %s error\n' % hddSectors
    FcgUtils.create_table(groupName, dmTable)
    cacheName = 'cache_' + groupName
    cmd = 'flashcache_create -p back -b 4k -s %s %s %s /dev/mapper/%s' % (cacheSize, cacheName, cacheDev, groupName)
    FcgUtils.os_execue(cmd)

    freeTable = '0 %s linear /dev/mapper/%s 0\n'%(hddSectors, cacheName)
    freeName = 'free_' + groupName
    FcgUtils.create_table(freeName, freeTable)

def create_group(groupName, cacheDev):
    hddSize = '1P'
    cacheSize = int(FcgUtils.get_dev_sector_count(cacheDev))
    cacheSize = str(FcgUtils.sectors2Mb(cacheSize))
    __create_group(groupName, cacheDev, hddSize, cacheSize)

if __name__ == '__main__':
    groupName, cacheDev = parse_args(sys.argv[1:])
    create_group(groupName, cacheDev)

