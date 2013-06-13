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

def show_group(groupName):
    cmd = 'dmsetup table %s' % groupName
    groupTable = FcgUtils.os_execue(cmd)
    hardDisks = []
    cachedHardDisks = []
    for groupLine in groupTable.split('\n'):
        groupLine = groupLine.split()
        if len(groupLine) == 5:
            startGroupSec, offsetGroup, typeGroup, oriGroupDev, oriGroupStartSec = groupLine
            startGroupSec, offsetGroup, oriGroupStartSec = map(int, [startGroupSec, offsetGroup, oriGroupStartSec])
            oriGroupDev = FcgUtils.get_devname_from_major_minor(oriGroupDev)
            hardDisks.append(oriGroupDev)
            cachedHardDisk = '/dev/mapper/cache_%s' % oriGroupDev.split('/')[-1:][0]
            cachedHardDisks.append(cachedHardDisk)
    print 'Flashcache group name:', groupName
    print 'Consists of hard disks:'
    print '\t', '\t'.join(hardDisks)
    print 'Serves following cached disks:'
    print '\t', '\t'.join(cachedHardDisks)
    

if __name__ == '__main__':
    groupName = parse_args(sys.argv[1:])
    show_group(groupName)
