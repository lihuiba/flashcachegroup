#!/usr/bin/env python


from libfcg.common import executor
from libfcg.common import processutils as putils
from libfcg import dmtable
from libfcg import utils
from libfcg.dmsetup import Dmsetup
from libfcg.flashcache import Flashcache

class FCG():

	def __init__(self, group_name):
		self.group_name = group_name

	def _ssd_name(self):
		return 'ssd_' + self.group_name

	def _cache_name(self):
		return 'cache_' + self.group_name

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
		found = False
		for i in range(len(lines)):
			line_str = lines[i]
			line = line_str.strip().split()
			start, offset = map(int, line[0:2])
			map_type = line[2]
			if not found and map_type == 'error' and offset >= sector:
				start_sector = start
				new_disk_line = '%d %d linear %s 0\n' % (start, sector, disk)
				new_group_table += new_disk_line
				if offset > sector:
					new_err_line = '%d %d error\n' %(start+sector, offset-sector)
					new_group_table += new_err_line
				found = True
			else:
				new_group_table += line_str
				new_group_table += '\n'

		cache_dev = dm.mapdev_prefix + self._cache_name()
		cached_table = '0 %d linear %s %d' % (sector, cache_dev, start_sector)

		dm.reload_table(self.group_name, new_group_table)
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
			line_start, line_offset = [int(x) for x in new_group_line[0:2]]
			line_type = new_group_line[2]
			if line_type == 'error':
				if pre_type == 'error':
					pre_offset += line_offset
				else:
					pre_start, pre_offset, pre_type = [line_start, line_offset, line_type]
			elif line_type == 'linear':
				if pre_type == 'error':
					temp_line = '{0} {1} error\n'.format(pre_start, pre_offset)
					new_group_table += temp_line
				new_group_table += new_group_line_str
				new_group_table += '\n'
				pre_start, pre_offset, pre_type = [line_start, line_offset, line_type]
		if pre_type == 'error':
			temp_line = '{0} {1} error\n'.format(pre_start, pre_offset)
			new_group_table += temp_line

		cache_name = self._cache_name()
		cache_dev = dm.mapdev_prefix + cache_name
		cache_table = dm.get_table(cache_name)
		fc = Flashcache()
		block_size = fc.get_block_size(cache_table)
		start_blk, offset_blk = utils.sector_offset2block_offset(cachedev_offset, offset, block_size)
		fc.invalid(cache_dev, start_blk, offset_blk)
		dm.remove_table(cached_name)
		dm.reload_table(self.group_name, new_group_table)

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

		fc = Flashcache()
		cache_name = self._cache_name()
		cache_table = dm.get_table(cache_name)
		ssd_dev = fc.get_ssd_dev(cache_table)
		dm.remove_table(cache_name)
		fc.destroy(ssd_dev)

		dm.remove_table(self._ssd_name())
		dm.remove_table(self.group_name)
