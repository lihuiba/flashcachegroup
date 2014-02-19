#!/usr/bin/env python

import tempfile

from common import processutils as putils

def execute(cmd, *args, **kwargs):
	(out, ret) = putils.execute(cmd, *args, **kwargs)
	out = out.strip()
	return out

def get_dev_sector_count(dev):
	devSector = execute('blockdev', '--getsz', dev)
	if type(devSector) != int:
		try:
			devSector = int(devSector)
		except:
			return 0
	return devSector

def write2tempfile(content):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    temp.close()
    return temp.name

if __name__ == '__main__':
	print get_dev_sector_count('/dev/sda5')
