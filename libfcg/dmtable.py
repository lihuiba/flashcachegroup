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

def insert_disk_to_linear_table(table, disk):
	pass

def remove_disk_from_linear_table(table, disk):
	pass
