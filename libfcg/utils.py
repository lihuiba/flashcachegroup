#!/usr/bin/env python

import tempfile

from common import processutils as putils

def execute(cmd, *args, **kwargs):
	print args
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

def bytes_str2bytes_count(bytes):
	#take M as default
	bytes_num = 0
	if bytes.endswith('P') or bytes.endswith('p'):
		bytes_num = int(bytes[:-1])*1024*1024*1024*1024*1024
	elif bytes.endswith('T') or bytes.endswith('t'):
		bytes_num = int(bytes[:-1])*1024*1024*1024*1024
	elif bytes.endswith('G') or bytes.endswith('g'):
		bytes_num = int(bytes[:-1])*1024*1024*1024
	elif bytes.endswith('M') or bytes.endswith('m'):
		bytes_num = int(bytes[:-1])*1024*1024
	elif bytes.endswith('K') or bytes.endswith('k'):
		bytes_num = int(bytes[:-1])*1024
	else:
		bytes_num = int(bytes)*1024*1024
	return bytes_num

def bytes2sectors(bytes):
	bytes = bytes_str2bytes_count(bytes)
	sectors = bytes/512
	return sectors

def sector_offset2block_offset(startSector, offset, blkSize):
	blkSize = bytes_str2bytes_count(blkSize)
	startBlk = startSector * 512 / blkSize
	offsetBlk = offset * 512 / blkSize
	return startBlk, offsetBlk

def sectors2MB(sectors):
	return str(sectors*512/1024/1024) + 'M'

if __name__ == '__main__':
	print get_dev_sector_count('/dev/sda5')
