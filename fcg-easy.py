#!/usr/bin/env python
import sys, os, commands, tempfile, hashlib

def _index(alist, element):
    try:
        index = alist.index(element)
        return index
    except:
        return -1

def parse_args(cmdline):
    groupName = ''
    groupIndex = max(_index(cmdline, '-g'), _index(cmdline, '--group'))
    groupName = cmdline[groupIndex+1]
    cmdline.remove(cmdline[groupIndex])
    cmdline.remove(groupName)

    hddIndex = max(_index(cmdline, '-h'), _index(cmdline, '--hdddev'))
    cacheIndex = max(_index(cmdline, '-c'), _index(cmdline, '--cachedev'))
    hddDevs = []
    cacheDevs = []
    if hddIndex < cacheIndex:
        hddDevs = cmdline[hddIndex+1:cacheIndex]
        cacheDevs = cmdline[cacheIndex+1:]
    else:
        hddDevs = cmdline[hddIndex+1:]
        cacheDevs = cmdline[cacheIndex+1:hddIndex] 
    if groupName == '' or len(hddDevs) == 0 or len(cacheDevs) == 0:
        sys.exit()
    return groupName, hddDevs, cacheDevs

def _os_execute(cmd):
    ret, output = commands.getstatusoutput(cmd)
    if ret == '0' or ret == 0:
        return output
    else:
        raise Exception(output)

def _get_dev_sector_count(dev):
    # try /dev/block/xxx/size
    cmd = 'blockdev --getsz %s'%dev
    devSector = _os_execute(cmd)
    if type(devSector) != int:
        try:
            devSector = int(devSector)
        except:
            return 0
    return devSector

def _sectors2MB(sectors):
    return str(sectors*512/1024/1024) + 'M'

def _linear_map_table(devices):
    table = ''
    startSector = 0
    for device in devices:
        if not os.path.exists(device):
            raise Exception('Device %s does NOT exist...' % device)
        sector = _get_dev_sector_count(device)
        if sector <= 0:
            raise Exception('Device %s is EMPTY...' % device)
        table +=  '%d %d linear %s 0\n' % (startSector, sector, device)
        startSector += sector
    return table

def _write2tempfile(content):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    temp.close()
    return temp.name

def _create_table(name, table):
    tmpTableFile = _write2tempfile(table)
    cmd = 'dmsetup create %s %s' % (name, tmpTableFile)
    try:
        _os_execute(cmd)
        return True
    except Exception, ErrMsg:
        print cmd + ': ',
        print ErrMsg
        return False

def _delete_table(name):
    cmd = 'dmsetup remove %s' % name
    try:
        _os_execute(cmd)
        return True
    except Exception, ErrMsg:
        print cmd + ': ',
        print ErrMsg
        return False

def _create_flashcache(cacheName, cacheDevice, groupDevice):
    cacheSize = _sectors2MB(_get_dev_sector_count(cacheDevice))
    cmd = 'flashcache_create -p back -b 4k -s %s %s %s %s' % (cacheSize, cacheName, cacheDevice, groupDevice)
    try:
        _os_execute(cmd)
        return True
    except Exception, ErrMsg:
        print cmd + ': ',
        print ErrMsg
        return False

def _get_device_name(device):
    name = device.split('/')[-1:][0]
    return name

def _cached_tables(devices, cacheGroupDevice):
    names = []
    tables = []
    startSector = 0
    for device in devices:
        name = 'cached-' + _get_device_name(device) 
        names.append(name)
        sector = _get_dev_sector_count(device)
        table = '0 %d linear %s %d\n' % (sector, cacheGroupDevice, startSector)
        tables.append(table)
        startSector += sector
    assert len(names) == len(tables), 'Something BAD happened when try to get cached tables...'
    return names, tables

def create_group(groupName, hddDevs, cacheDevs):
    #create linear device group
    groupTable = ''
    try:
        groupTable = _linear_map_table(hddDevs)
    except Exception, e:
        print e
        return

    cacheDevTable = ''
    try:
        cacheDevTable = _linear_map_table(cacheDevs)
    except Exception, e:
        print e
        return

    cacheDevName = 'cachedevices-%s' % groupName

    ret =  _create_table(groupName, groupTable)
    if ret == False:
        return
    ret = _create_table(cacheDevName, cacheDevTable)
    if ret == False:
        _delete_table(groupName)
        return

    #create flashcache
    groupDevice = '/dev/mapper/%s' % groupName
    cacheDevice = '/dev/mapper/%s' % cacheDevName
    cacheName = 'cachegroup-%s' % groupName
    ret = _create_flashcache(cacheName, cacheDevice, groupDevice)
    if ret == False:
        _delete_table(groupName)
        _delete_table(cacheDevName)
        return

    #create cached devices
    cacheGroupDevice = '/dev/mapper/%s' % cacheName
    cachedNames, cachedTables = _cached_tables(hddDevs, cacheGroupDevice)
    for i in range(len(cachedNames)):
        _create_table(cachedNames[i], cachedTables[i])
        
if __name__ == '__main__':
    groupName, hddDevs, cacheDevs = parse_args(sys.argv[1:])
    create_group(groupName, hddDevs, cacheDevs)

