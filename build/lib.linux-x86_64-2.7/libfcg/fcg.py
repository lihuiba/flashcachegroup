#!/usr/bin/env python

import os

from pydm.dmsetup import Dmsetup
from pydm.dmtable import LinearTable
from pydm.disk import Disk
from libfcg.common import executor
from libfcg.common import processutils as putils
from libfcg import utils
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
        hdd = Disk.from_error(hdd_sectors)
        hdd_group = LinearTable.from_disks(group_name, [hdd])

        ssd_name = self._ssd_name()
        ssd_group = LinearTable.from_disks(ssd_name, ssds)

        fc = Flashcache()
        cache_name = self._cache_name()
        cache_Dev = fc.create(cache_name, ssd_group.path, hdd_group.path, block_size, pattern)

    def add_disk(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        disk = Disk.from_path(disk_path)
        hdd_group = LinearTable(self.group_name)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name

        hdd_group.insert_disk(disk)
        dm = Dmsetup() 
        cache_dev = dm.mapdev_prefix + self._cache_name()
        cached_table = '0 %d linear %s %d' % (disk.size, cache_dev, disk.start)
        cached_disk_name = self._cached_disk_name(disk.dev)

        dm.create_table(cached_disk_name, cached_table)
        return dm.mapdev_prefix + cached_disk_name

    def rm_disk(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        hdd_group = LinearTable(self.group_name)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        disk = hdd_group.find_disk(disk_path)

        dm = Dmsetup()
        cached_name = self._cached_disk_name(disk.dev)

        cache_name = self._cache_name()
        cache_dev = dm.mapdev_prefix + cache_name
        cache_table = dm.get_table(cache_name)
        fc = Flashcache()
        block_size = fc.get_block_size(cache_table)
        start_blk, offset_blk = utils.sector_offset2block_offset(disk.start, disk.size, block_size)
        fc.invalid(cache_dev, start_blk, offset_blk)

        dm.remove_table(cached_name)
        hdd_group.remove_disk(disk)

    def delete_group(self):
        hdd_group = LinearTable(self.group_name)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        dm = Dmsetup()
        #TODO: check for wether busy
        for disk in hdd_group.disks:
            if disk.mapper != 'error':
                cached_name = self._cached_disk_name(disk.dev)
                dm.remove_table(cached_name)

        fc = Flashcache()
        cache_name = self._cache_name()
        cache_table = dm.get_table(cache_name)
        ssd_dev = fc.get_ssd_dev(cache_table)
        dm.remove_table(cache_name)
        fc.destroy(ssd_dev)

        dm.remove_table(self._ssd_name())
        dm.remove_table(self.group_name)
