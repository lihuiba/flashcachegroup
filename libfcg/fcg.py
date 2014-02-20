#!/usr/bin/env python


from common import executor
from common import processutils as putils
import dmtable
import utils
from  dmsetup import Dmsetup
from flashcache import Flashcache

class FCG():

	def __init__(self, group_name):
		self.group_name = group_name

	def _ssd_name(self):
		return 'ssd_' + self.group_name

	def _cache_name(self):
		return 'cache_' + self.group_name

	def _free_name(self):
		return 'free_' + self.group_name

	def _cached_disk_name(self, disk):
		prefix = 'cached_'
		if disk.find('/') >= 0:
			return prefix + disk.split('/')[-1]
		else:
			return prefix + disk

	def create_group(self, ssds, block_size, pattern):
		#TODO: roll back if failed
		group_name = self.group_name
		dm = Dmsetup()
		hdd_size = '1P'
		hdd_sectors = utils.bytes2sectors(hdd_size)
		group_table = dmtable.get_error_table(hdd_sectors)
		group_dev = dm.create_table(group_name, group_table)

		ssd_name = self._ssd_name()
		ssd_linear_table = dmtable.linear_map_table(ssds)
		ssd_dev = dm.create_table(ssd_name, ssd_linear_table)

		fc = Flashcache()
		cache_name = self._cache_name()
		cache_Dev = fc.create(cache_name, ssd_dev, group_dev, block_size, pattern)

		free_name = self._free_name()
		free_table = dmtable.linear_map_table([cache_Dev])
		dm.create_table(free_name, free_table)
	

	def _get_free_table(self, group_table, cache_Dev):
		free_table = ''
		lines = group_table.strip().split('\n')
		start = 0
		for line_str in lines:
			line = line_str.strip().split()
			line_start, line_offset = map(int, line[0:2])
			if len(line) == 3 and line[2] == 'error':
				new_line = '{0} {1} linear {2} {3}\n'.format(start, line_offset, cache_Dev, line_start)
				free_table += new_line
				start += line_offset
		return free_table

	def add_disk(self, disk):
		dm = Dmsetup()
		group_table = ''
		try:
			group_table = dm.get_table(self.group_name)
		except Exception, e:
			raise Exception("Group %s dose NOT exist..." % self.group_name)
		new_group_table = ''
		start_sector = 0
		sector = utils.get_dev_sector_count(disk)
		lines = group_table.strip().split('\n')
		for i in range(len(lines)):
			line_str = lines[i]
			line = line_str.strip().split()
			start, offset = map(int, line[0:2])
			map_type = line[2]
			if map_type == 'error' and offset >= sector:
				start_sector = start
				new_disk_line = '%d %d linear %s 0\n' % (start, sector, disk)
				new_group_table += new_disk_line
				if offset > sector:
					new_err_line = '%d %d error\n' %(start+sector, offset-sector)
					new_group_table += new_err_line
			else:
				new_group_table += line_str
				new_group_table += '\n'
		cache_dev = dm.mapdev_prefix + self._cache_name()
		new_free_table = self._get_free_table(new_group_table, cache_dev)
		cached_table = '0 %d linear %s %d' % (sector, cache_dev, start_sector)

		dm.reload_table(self.group_name, new_group_table)
		dm.reload_table(self._free_name(), new_free_table)
		dm.create_table(self._cached_disk_name(disk), cached_table)

	def rm_disk(self, disk):
		dm = Dmsetup()
		group_table = ''
		try:
			group_table = dm.get_table(self.group_name)
		except Exception, e:
			raise Exception("Group %s dose NOT exist..." % self.group_name)
		cached_name = self._cached_disk_name(disk)
		cached_table = dm.get_table(cached_name)
		cached_line = cached_table.strip().split()
		start, offset, cachedev_offset = map(int, [cached_line[0], cached_line[1], cached_line[4]])

		new_group_lines = []
		group_lines = group_table.split('\n')
		for group_line_str in group_lines:
			group_line = group_line_str.strip().split()
			group_line_start, group_line_offset = map(int, group_line[0:2])
			if len(group_line) == 5 and group_line_offset == offset:
					mapped_disk = group_line[3]
					try:
						major, minor = [int(x) for x in mapped_disk.split(':')]
						mapped_disk = utils.get_devname_from_major_minor(mapped_disk)
					except:
						pass
					if mapped_disk == disk:
						new_error_line = '{0} {1} error'.format(group_line_start, group_line_offset)
						new_group_lines.append(new_error_line)
					else:
						new_group_lines.append(group_line_str)
			else:
				new_group_lines.append(group_line_str)

		#adjust lines
		pre_type = ''
		pre_start = 0
		pre_offset = 0
		new_group_table = ''
		for new_group_line_str in new_group_lines:
			new_group_line = new_group_line_str.strip().split()
			if len(new_group_line) == 3:
				#TODO: to be continued
			pre_type = group_line[2]
			pre_start = group_line_start
			pre_offset = group_line_offset

		cache_dev = dm.mapdev_prefix + self._cache_name()
		new_free_table = self._get_free_table(new_group_table, cache_dev)

		dm.remove_table(cached_name)
		dm.reload_table(self.group_name, new_group_table)
		dm.reload_table(self._free_name(), new_free_table)

	def delete_group(self):
		dm = Dmsetup()
		group_table = ''
		try:
			group_table = dm.get_table(self.group_name)
		except Exception, e:
			raise Exception("Group %s dose NOT exist..." % self.group_name)
		disks = dmtable.get_disks_in_linear_table(group_table)
		#TODO: check for wether busy
		for disk in disks:
			cached_name = self._cached_disk_name(disk)
			dm.remove_table(cached_name)

		dm.remove_table(self._free_name())

		fc = Flashcache()
		cache_name = self._cache_name()
		cache_table = dm.get_table(cache_name)
		ssd_dev = fc.get_ssd_dev(cache_table)
		dm.remove_table(cache_name)
		fc.destroy(ssd_dev)

		dm.remove_table(self._ssd_name())
		dm.remove_table(self.group_name)
