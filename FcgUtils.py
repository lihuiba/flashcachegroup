#!/usr/bin/env python
import commands, tempfile
def bytes2sectors(bytes):
    if bytes.endswith('T') or bytes.endswith('t'):
        bytes = int(bytes[:-1])*1024*1024*1024*1024
    elif bytes.endswith('G') or bytes.endswith('g'):
        bytes = int(bytes[:-1])*1024*1024*1024
    elif bytes.endswith('M') or bytes.endswith('m'):
        bytes = int(bytes[:-1])*1024*1024
    elif bytes.endswith('K') or bytes.endswith('k'):
        bytes = int(bytes[:-1])*1024
    else:
        bytes = int(bytes)*1024*1024
    sectors = bytes/512
    return sectors

def sectors2Mb(sectors):
    return str(sectors*512/1024/1024) + 'M'

def os_execue(cmd):
    try:
        ret, output = commands.getstatusoutput(cmd)
        if ret == '0' or ret == 0:
            return output
        else:
            raise 'Execute %s failed...'%cmd
    except Exception, e:
        print e
        print 'Execute %s failed!' % cmd
        return None

def write2tempfile(content):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    temp.close()
    return temp.name

def get_devname_from_major_minor(majorMinor):
    cmd = "ls -l /dev/block|awk '{print $9, $11}'|grep %s" % majorMinor
    _, deviceName = os_execue(cmd).split()
    deviceName = deviceName.split('/')[-1:][0]
    if majorMinor.split(':')[0] == '253':
        cmd = "ls -l /dev/mapper|awk '{if ($11 != \"\") print $11, $9}'|grep %s"% deviceName
        _, deviceName = os_execue(cmd).split()
        return '/dev/mapper/%s' % deviceName   
    else:
        return '/dev/%s' % deviceName

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

def delete_table(tableName):
    cmd = 'dmsetup remove %s'%tableName
    os_execue(cmd)

def test_get_devname_from_major_minor():
    for mm in ['7:2', '253:5']:
        print get_devname_from_major_minor(mm)

if __name__ == '__main__':
    test_get_devname_from_major_minor()
