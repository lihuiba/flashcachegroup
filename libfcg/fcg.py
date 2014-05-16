#!/usr/bin/env python

import os
import time

from pydm.dmsetup import Dmsetup
from pydm.disk import Disk

from libfcg import utils
from libfcg.flashcache import Flashcache
from libfcg.table import FcgLinearTable


class FCG():

    def __init__(self, group_name, root_helper=''):
        self.group_name = group_name
        self.root_helper = root_helper

    @property
    def _ssd_name(self):
        return 'ssd_' + self.group_name

    @property
    def _cache_name(self):
        return 'cache_' + self.group_name

    @staticmethod
    def _cached_disk_name(disk):
        prefix = 'cached_'
        if disk.find('/') >= 0:
            return prefix + disk.split('/')[-1]
        else:
            return prefix + disk

    def is_valid(self):
        dm = Dmsetup(root_helper=self.root_helper)
        existences = map(dm.is_exist, [self.group_name, self._ssd_name, self._cache_name])
        if reduce(lambda x, y: x and y, existences):
            return True
        else:
            if reduce(lambda x, y: x or y, existences):
                raise Exception("Cache group has been broken!")
            else:
                return False

    def create_group(self, ssds, block_size, pattern):
        #TODO: roll back if failed
        group_name = self.group_name
        hdd_size = '1P'
        hdd_sectors = utils.bytes2sectors(hdd_size)
        hdd = Disk.from_error(hdd_sectors, root_helper=self.root_helper)
        hdd_group = FcgLinearTable.from_disks(group_name, [hdd], root_helper=self.root_helper)

        ssd_name = self._ssd_name
        ssd_group = FcgLinearTable.from_disks(ssd_name, ssds,  root_helper=self.root_helper)

        fc = Flashcache(root_helper=self.root_helper)
        cache_name = self._cache_name
        cache_dev = fc.create(cache_name, ssd_group.path, hdd_group.path, block_size, pattern)
        return cache_dev

    def add_disk(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        disk = Disk.from_path(disk_path, root_helper=self.root_helper)
        hdd_group = FcgLinearTable(self.group_name, root_helper=self.root_helper)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name

        hdd_group.insert_disk(disk)
        dm = Dmsetup(root_helper=self.root_helper)
        cache_dev = dm.mapdev_prefix + self._cache_name
        cached_table = '0 %d linear %s %d' % (disk.size, cache_dev, disk.start)
        cached_disk_name = self._cached_disk_name(disk.dev)

        dm.create_table(cached_disk_name, cached_table)
        return dm.mapdev_prefix + cached_disk_name

    def rm_disk(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        hdd_group = FcgLinearTable(self.group_name, root_helper=self.root_helper)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        disk = hdd_group.find_disk(disk_path)
        dm = Dmsetup(root_helper=self.root_helper)
        cached_name = self._cached_disk_name(disk.dev)
        dm.remove_table(cached_name)
        hdd_group.remove_disk(disk)

    def delete_group(self):
        hdd_group = FcgLinearTable(self.group_name, root_helper=self.root_helper)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        dm = Dmsetup(root_helper=self.root_helper)
        #TODO: check for wether busy
        for disk in hdd_group.disks:
            if disk.mapper != 'error':
                cached_name = self._cached_disk_name(disk.dev)
                dm.remove_table(cached_name)

        fc = Flashcache(root_helper=self.root_helper)
        cache_name = self._cache_name
        cache_table = dm.get_table(cache_name)
        ssd_dev = fc.get_ssd_dev(cache_table)
        dm.remove_table(cache_name)
        fc.destroy(ssd_dev)

        time.sleep(0.1)

        dm.remove_table(self._ssd_name)
        dm.remove_table(self.group_name)
