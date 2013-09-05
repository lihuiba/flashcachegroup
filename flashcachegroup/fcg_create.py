#!/usr/bin/env python
import sys, os
import FcgUtils
from FcgTable import FcgTable
from FcgCache import FcgCacheGroup

def __create_group(groupName, cacheDev, hddSize, cacheSize):
    #create group table
    groupTable = FcgTable(groupName)
    if groupTable.is_existed():
        print 'Group %s has been already existed...' % groupName
        return False

    hddSectors = FcgUtils.bytes2sectors(hddSize)
    dmTable = '0 %d error' % hddSectors
    groupTable.set_lines(dmTable)
    ret = groupTable.create()
    if ret == False:
        print 'Create group %s failed...' % groupName
        return False

    #create cache device
    cacheName = 'cache_' + groupName
    cacheGroup = FcgCacheGroup(cacheName)
    ret = cacheGroup.create(groupName, cacheDev, cacheSize)
    if ret == False:
        groupTable.delete()
        return False

    #create free table
    freeTable = FcgTable('free_' + groupName)
    dmTable = '0 %s linear /dev/mapper/%s 0'%(hddSectors, cacheName)
    freeTable.set_lines(dmTable)
    ret = freeTable.create()
    if ret == False:
        cacheGroup.delete()
        groupTable.delete()
        return False
    return True
        

def create_group(groupName, cacheDev):
    hddSize = '1P'
    if not os.path.exists(cacheDev):
        print 'Cache device %s does NOT exist...' % cacheDev
        return 
    cacheSize = int(FcgUtils.get_dev_sector_count(cacheDev))
    if cacheSize <= 0:
        print "Cache device should NOT be empty..."
        return 
    cacheSize = str(FcgUtils.sectors2MB(cacheSize))
    __create_group(groupName, cacheDev, hddSize, cacheSize)
