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
		sector = utils.get_dev_sector_count(disk)
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

def insert_disk_to_linear_table(disk, table):
	new_table = ''
	sector = utils.get_dev_sector_count(disk)
	lines = table.strip().split('\n')
	for i in range(len(lines)):
		line_str = lines[i]
		line = line_str.strip().split()
		start, offset = map(int, line[0:2])
		map_type = line[2]
		if map_type == 'error' and offset >= sector:
			new_disk_line = '%d %d linear %s 0\n' % (start, sector, disk)	
			new_table += new_disk_line
			if offset > sector:
				new_err_line = '%d %d error\n' %(start+sector, offset-sector)
				new_table += new_err_line
		else:
			new_table += line_str
			new_table += '\n'
	return new_table
				
