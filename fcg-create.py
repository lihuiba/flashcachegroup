#!/usr/bin/env python
import sys, getopt
import FcgUtils
from FcgTable import FcgTable

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
    #create group table
    groupTable = FcgTable(groupName)
    hddSectors = FcgUtils.bytes2sectors(hddSize)
    dmTable = '0 %d error' % hddSectors
    groupTable.set_lines(dmTable)
    groupTable.create()
    #create cache device
    cacheName = 'cache_' + groupName
    cmd = 'flashcache_create -p back -b 4k -s %s %s %s /dev/mapper/%s' % (cacheSize, cacheName, cacheDev, groupName)
    FcgUtils.os_execue(cmd)
    #create free table
    freeTable = FcgTable('free_' + groupName)
    dmTable = '0 %s linear /dev/mapper/%s 0'%(hddSectors, cacheName)
    freeTable.set_lines(dmTable)
    freeTable.create()

def create_group(groupName, cacheDev):
    hddSize = '1P'
    cacheSize = int(FcgUtils.get_dev_sector_count(cacheDev))
    cacheSize = str(FcgUtils.sectors2Mb(cacheSize))
    __create_group(groupName, cacheDev, hddSize, cacheSize)

if __name__ == '__main__':
    groupName, cacheDev = parse_args(sys.argv[1:])
    create_group(groupName, cacheDev)

