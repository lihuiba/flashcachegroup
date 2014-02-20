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
		if disk.contais('/'):
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
	

	def add_disk(self):
		pass

	def rm_disk(self):
		pass

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
