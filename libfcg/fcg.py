#!/usr/bin/env python


from common import executor
import dmtable
from  dmsetup import Dmsetup
from flashcache import Flashcache

class FCG(executor.Executor):
	def __init__(self, cmd, root_helper, execute):
		super(FCG, self).__init__(root_helper, execute=execute)
		self._cmd = cmd

	def _run(self, *args, **kwargs):
		self._execute(self._cmd, *args, run_as_root=True, **kwargs)

	def create_group(self, group_name, ssds, block_size, pattern):
		dm = Dmsetup()
		hdd_size = '1P'
		hdd_sectors = utils.bytes2sectors(hdd_size)
		group_table = dmtable.get_error_table(hdd_sectors)
		group_dev = dm.create_table(group_name, group_table)
		
		ssd_name = 'ssd_' + group_name
		ssd_linear_table = dmtable.linear_map_table(ssds)
		ssd_dev = dm.create_table(ssd_name, ssd_linear_table)

		fc = Flashcache()
		cache_name = 'cache_' + group_name
		cache_Dev = fc.create(cache_name, ssd_dev, group_dev, block_size, pattern)

		free_name = 'free_' + group_name
		free_table = dmtable.linear_map_table(cache_Dev)
		dm.create_table(free_name, free_table)
	

	def add_disk(self):
		pass

	def rm_disk(self):
		pass

	def delete_group(self):
		pass
