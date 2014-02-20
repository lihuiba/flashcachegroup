#!/usr/bin/env python

import os
import utils

def get_error_table(sectors):
	table = '0 %d error' % sectors
	return table

def linear_map_table(disks):
	table = ''
	startSector = 0
	for disk in disks:
		if not os.path.exists(disk):
			raise Exception('Device %s does NOT exist...' % disk)
		sector = utils.get_dev_sector_count(disk)
		if sector <= 0:
			raise Exception('Device %s is EMPTY...' % disk)
		table +=  '%d %d linear %s 0\n' % (startSector, sector, disk)
		startSector += sector
	return table

def get_disks_in_linear_table(table):
	disks = []
	table_list = table.split('\n')
	for table_line_str in table_list:
		line = table_line_str.split()
		if len(line) == 5:
			disk = line[3]
			try:
				major, minor = [int(x) for x in disk.split(':')]
				disk = utils.get_devname_from_major_minor(disk)
			except Exception, e:
				pass
			disks.append(disk)
	return disks
