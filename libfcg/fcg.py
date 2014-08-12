#!/usr/bin/env python

import os
import time

from pydm.dmsetup import Dmsetup
from pydm.disk import Disk
from pydm.dmlinear import DmLinearTable

from libfcg import utils
from libfcg.flashcache import Flashcache
from libfcg.common.chain import Chain


class FCG():
    def __init__(self, group_name, root_helper=''):
        self.group_name = group_name
        self.root_helper = root_helper
        self.hdd_group = None
        self.ssd_group = None
        self.flashcache = None
        self.cache_dev = ''

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

    def _exists(self, fcg_table, disk):
        dm = Dmsetup(root_helper=self.root_helper)
        cached_disk_name = self._cached_disk_name(disk.dev)
        return fcg_table.exists(disk) and dm.is_exist(cached_disk_name)

    def exists(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        disk = Disk.from_path(disk_path, root_helper=self.root_helper)
        hdd_group = DmLinearTable(self.group_name, root_helper=self.root_helper)
        assert hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        return self._exists(hdd_group, disk)

    def _create_hdd_group(self):
        group_name = self.group_name
        hdd_size = '1P'
        hdd_sectors = utils.bytes2sectors(hdd_size)
        hdd = Disk.from_error(hdd_sectors, root_helper=self.root_helper)
        self.hdd_group = DmLinearTable.from_disks(group_name, [hdd], root_helper=self.root_helper)

    def _create_ssd_group(self, ssds):
        ssd_name = self._ssd_name
        self.ssd_group = DmLinearTable.from_disks(ssd_name, ssds, root_helper=self.root_helper)

    def _create_cache_group(self, block_size, pattern):
        self.flashcache = Flashcache(root_helper=self.root_helper)
        cache_name = self._cache_name
        self.cache_dev = self.flashcache.create(cache_name, self.ssd_group.path, self.hdd_group.path, block_size, pattern)

    def _destroy_cache(self):
        dm = Dmsetup(root_helper=self.root_helper)
        cache_name = self._cache_name
        cache_table = dm.get_table(cache_name)
        ssd_dev = self.flashcache.get_ssd_dev(cache_table)
        dm.remove_table(cache_name)
        self.flashcache.destroy(ssd_dev)

    def create_group(self, ssds, block_size, pattern):
        create_chain = Chain()
        create_chain.add_step(lambda: self._create_hdd_group(), lambda: self.hdd_group.remove_table())
        create_chain.add_step(lambda: self._create_ssd_group(ssds), lambda: self.ssd_group.remove_table())
        create_chain.add_step(lambda: self._create_cache_group(block_size, pattern), lambda: self._destroy_cache())
        create_chain.do()
        return self.cache_dev

    def add_disk(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        disk = Disk.from_path(disk_path, root_helper=self.root_helper)
        if not self.hdd_group:
            self.hdd_group = DmLinearTable(self.group_name, root_helper=self.root_helper)
        assert self.hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        if not self.hdd_group.exists(disk):
            self.hdd_group.append_disk(disk)
        dm = Dmsetup(root_helper=self.root_helper)
        cached_disk_name = self._cached_disk_name(disk.dev)
        if not dm.is_exist(cached_disk_name):
            cache_dev = dm.mapdev_prefix + self._cache_name
            cached_table = '0 %d linear %s %d' % (disk.size, cache_dev, disk.start)
            dm.create_table(cached_disk_name, cached_table)
        return dm.mapdev_prefix + cached_disk_name

    def rm_disk(self, disk_path):
        if os.path.islink(disk_path):
            disk_path = os.path.realpath(disk_path)
        if not self.hdd_group:
            self.hdd_group = DmLinearTable(self.group_name, root_helper=self.root_helper)
        assert self.hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        disk = self.hdd_group.find_disk(disk_path)
        dm = Dmsetup(root_helper=self.root_helper)
        cached_name = self._cached_disk_name(disk.dev)
        dm.remove_table(cached_name)
        self.hdd_group.remove_disk(disk)

    def delete_group(self):
        if not self.hdd_group:
            self.hdd_group = DmLinearTable(self.group_name, root_helper=self.root_helper)
        assert self.hdd_group.existed, "Group %s dose NOT exist..." % self.group_name
        dm = Dmsetup(root_helper=self.root_helper)
        # TODO: check for wether busy
        for disk in self.hdd_group.disks:
            if disk.mapper != 'error':
                cached_name = self._cached_disk_name(disk.dev)
                dm.remove_table(cached_name)

        self._destroy_cache()

        time.sleep(0.1)

        dm.remove_table(self._ssd_name)
        dm.remove_table(self.group_name)
