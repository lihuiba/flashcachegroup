#!/usr/bin/env python

from common import executor
from common import processutils as putils
import utils


cachedev_prefix = '/dev/mapper/'

class Flashcache(executor.Executor):
	def __init__(self, execute=putils.execute):
		super(Dmsetup, self).__init__(root_helper='', execute=execute)

	def _run(self, *args, **kwargs):
		self._execute(self._cmd, *args, run_as_root=True, **kwargs)

	def create(self, cache_name, ssd_dev, group_dev, block_size, pattern):
		try:
			self.destroy(ssd_dev)
		except Exception, e:
			pass

		cache_size = utils.sector2MB(utils.get_dev_sector_count(ssd_dev))
		self._run('flashcache_create', '-p', pattern, '-b', block_size, '-s', cache_size, cache_name, ssd_dev, froup_dev)
		return cachedev_prefix + cache_name
		
	def destroy(self, ssd_dev):
		self._run('flashcache_destroy', '-f', ssd_dev)
