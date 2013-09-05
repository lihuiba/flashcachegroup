#!/usr/bin/env python
import sys, getopt
import FcgUtils
from FcgTable import FcgTable

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
    groupTable = FcgTable(groupName)
    if not groupTable.is_existed():
        print 'Group %s does NOT exist...' % groupName
        return False

    hardDisks = []
    for line in groupTable.lines:
        if line['type'] == 'linear':
            hardDisks.append(line['oriDev'])

    print 'Flashcache group name:', groupName
    print 'Consists of following hard disks:'
    print '\t', '\t'.join(hardDisks)
    
if __name__ == '__main__':
    groupName = parse_args(sys.argv[1:])
    show_group(groupName)
