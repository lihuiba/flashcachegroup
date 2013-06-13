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
    print groupTable

if __name__ == '__main__':
    groupName = parse_args(sys.argv[1:])
    show_group(groupName)
