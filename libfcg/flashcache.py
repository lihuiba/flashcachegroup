#!/usr/bin/env python

from libfcg.common import executor
from libfcg.common import processutils as putils
from libfcg import utils


cachedev_prefix = '/dev/mapper/'

class Flashcache(executor.Executor):
	def __init__(self, execute=putils.execute):
		super(Flashcache, self).__init__(root_helper='', execute=execute)

	def _run(self, cmd, *args, **kwargs):
		self._execute(cmd, *args, run_as_root=True, **kwargs)

	def create(self, cache_name, ssd_dev, group_dev, block_size, pattern):
		try:
			self.destroy(ssd_dev)
		except Exception, e:
			pass

		cache_size = utils.sectors2MB(utils.get_dev_sector_count(ssd_dev))
		self._run('flashcache_create', '-p', pattern, '-b', block_size, '-s', cache_size, cache_name, ssd_dev, group_dev)
		return cachedev_prefix + cache_name
		
	def destroy(self, ssd_dev):
		self._run('flashcache_destroy', '-f', ssd_dev)

	def get_ssd_dev(self, cache_table):
		left = cache_table.find('(') + 1
		right = cache_table.find(')')
		ssd_dev = cache_table[left:right]
		return ssd_dev
