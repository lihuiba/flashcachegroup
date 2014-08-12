#!/usr/bin/env python

from pydm.blockdev import Blockdev

from libfcg.common import executor
from libfcg.common import processutils as putils
from libfcg import utils

cachedev_prefix = '/dev/mapper/'


class Flashcache(executor.Executor):
    def __init__(self, root_helper='', execute=putils.execute):
        super(Flashcache, self).__init__(root_helper=root_helper, execute=execute)

    def _run(self, cmd, *args, **kwargs):
        self._execute(cmd, *args, run_as_root=True, root_helper=self._root_helper, **kwargs)

    def create(self, cache_name, ssd_dev, group_dev, block_size, pattern):
        try:
            self.destroy(ssd_dev)
        except Exception, e:
            pass

        block = Blockdev(root_helper=self._root_helper)

        cache_size = utils.sectors2MB(block.get_sector_count(ssd_dev))
        self._run('flashcache_create', '-p', pattern, '-b', block_size, '-s', cache_size, cache_name, ssd_dev, group_dev)
        return cachedev_prefix + cache_name
        
    def destroy(self, ssd_dev):
        self._run('flashcache_destroy', '-f', ssd_dev)

    def invalid(self, cache_dev, start, offset):
        self._run('flashcache_invalidate', cache_dev, start, offset)

    @staticmethod
    def _get_item(cache_table, item):
        location = cache_table.find(item)
        part_table = cache_table[location:]
        left = part_table.find('(') + 1
        right = part_table.find(')')
        content = part_table[left:right]
        return content

    def get_ssd_dev(self, cache_table):
        ssd_dev = self._get_item(cache_table, 'ssd dev')
        return ssd_dev

    def get_block_size(self, cache_table):
        block_size = self._get_item(cache_table, 'data block size')
        return block_size
