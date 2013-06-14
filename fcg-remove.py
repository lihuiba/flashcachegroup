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

def remove_hdd(groupName, hddDev):
    hddName = hddDev.split('/')[-1:][0]
    cacheHddName = 'cache_' + hddName
    cacheHddTabStr = FcgUtils.get_table_str(cacheHddName)
    cacheHddTabStruct = FcgUtils.get_table_struct_from_str(cacheHddTabStr)
    assert len(cacheHddTabStruct) == 1, 'Multi line found in table of %s' % cacheHddName
    cacheLine = cacheHddTabStruct[0]
    assert len(cacheLine) == 5, 'Could NOT support table format for %s\n Table is %s' % (cacheHddName, cacheHddTabStr)
    #delete cache_hdd table here
    FcgUtils.delete_table(cacheHddName)
    #invalid falshcache data of cache_hdd
    cacheGroupName = 'cache_%s' % groupName
    cacheGroupDev = '/dev/mapper/%s' % cacheGroupName
    cacheBlkSize = FcgUtils.get_cache_blksize(cacheGroupName)
    startBlk, offsetBlk = FcgUtils.sector_offset2block_offset(cacheLine['oriStartSec'], cacheLine['offset'], cacheBlkSize)
    FcgUtils.invalid_cache_blocks(cacheGroupDev, startBlk, offsetBlk) 
    #delete hdd line from group table
    groupTabStr = FcgUtils.get_table_str(groupName)
    groupTabStruct = FcgUtils.get_table_struct_from_str(groupTabStr)
    for i in range(len(groupTabStruct)):
        groupLine = groupTabStruct[i]
        if len(groupLine) == 5:
            if groupLine['offset'] == cacheLine['offset'] and groupLine['oriDev'] == hddDev:
                groupTabStruct[i] = {'startSec':groupLine['startSec'], 'offset':groupLine['offset'], 'type':'error'}
                break
    groupTabStruct = FcgUtils.adjust_table_strust(groupTabStruct)
    freeTabStruct = FcgUtils.get_free_table_from_group(groupTabStruct, cacheGroupDev)
    #reload group and free table 
    freeName = 'free_%s' % groupName
    groupTabStr = FcgUtils.get_table_str_from_struct(groupTabStruct)
    freeTabStr = FcgUtils.get_table_str_from_struct(freeTabStruct)
    FcgUtils.reload_table(groupName, groupTabStr)
    FcgUtils.reload_table(freeName, freeTabStr)

if __name__ == '__main__':
    groupName, hddDev = parse_args(sys.argv[1:])
    remove_hdd(groupName, hddDev)
