#!/usr/bin/env python
import commands, tempfile
def bytes2sectors(bytes):
    if bytes.endswith('G') or bytes.endswith('g'):
        bytes = int(bytes[:-1])*1024*1024*1024
    elif bytes.endswith('M') or bytes.endswith('m'):
        bytes = int(bytes[:-1])*1024*1024
    elif bytes.endswith('K') or bytes.endswith('k'):
        bytes = int(bytes[:-1])*1024
    else:
        bytes = int(bytes)*1024*1024
    sectors = bytes/512
    return sectors

def os_execue(cmd):
    try:
        ret, output = commands.getstatusoutput(cmd)
        if ret == '0' or ret == 0:
            return output
        else:
            raise 'Execute %s failed...'%cmd
    except:
        print 'Execute %s failed!' % cmd
        return None

def write2tempfile(content):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    temp.close()
    return temp.name

def get_dev_sector_count(dev):
    cmd = 'blockdev --getsz %s'%dev
    devSector = os_execue(cmd)
    if type(devSector) != int:
        devSector = int(devSector)
    return devSector

def create_table(tableName, tableContent):
    tmpTableFile = write2tempfile(tableContent) 
    cmd = 'dmsetup create %s %s' % (tableName, tmpTableFile)
    os_execue(cmd)

def reload_table(tableName, tableContent):
    cmd = 'dmsetup suspend %s'%tableName
    os_execue(cmd)
    tmpTableFile = write2tempfile(tableContent)
    cmd = 'dmsetup reload %s %s' % (tableName, tmpTableFile)
    os_execue(cmd)
    cmd = 'dmsetup resume %s'%tableName
    os_execue(cmd)
