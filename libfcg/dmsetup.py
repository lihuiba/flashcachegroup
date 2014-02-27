#!/usr/bin/env python

import os
from libfcg.common import executor
from libfcg.common import processutils as putils
from libfcg import utils
from libfcg import dmtable


class Dmsetup(executor.Executor):
    def __init__(self, mapdev_prefix = '/dev/mapper/', execute=putils.execute):
        super(Dmsetup, self).__init__(root_helper='', execute=execute)
        self.mapdev_prefix = mapdev_prefix

    def _run_dmsetup(self, dmsetup_command, *args):
        (out, err) = self._execute('dmsetup', dmsetup_command, *args,
                                    run_as_root=True)
        out = out.strip()
        return (out, err)

    def create_table(self, name, table):
        table_file = utils.write2tempfile(table)
        self._run_dmsetup('create', name, table_file)
        return self.mapdev_prefix + name

    def remove_table(self, name):
        self._run_dmsetup('remove', name)

    def reload_table(self, name, table):
        table_file = utils.write2tempfile(table)
        self._run_dmsetup('suspend', name)
        self._run_dmsetup('reload', name, table_file)
        self._run_dmsetup('resume', name)

    def show_table(self):
        (out, ret) = self._run_dmsetup('table')
        return out

    def get_table(self, name):
        (out, ret) = self._run_dmsetup('table', name)
        return out

    def snapshot(self, origin_name, origin_dev, snapshot_name, snapshot_dev):
        origin_size = utils.get_dev_sector_count(origin_dev)
        origin_table = '0 %d snapshot-origin %s' % (origin_size, origin_dev)
        snapshot_size = utils.get_dev_sector_count(snapshot_dev)
        snapshot_table = '0 %d snapshot %s %s N 128' % (origin_size, self.mapdev_prefix+origin_name, snapshot_dev)

        self.create_table(origin_name, origin_table)
        self.create_table(snapshot_name, snapshot_table)

    def multipath(self, disks):
        #:TODO
        pass

        

if __name__ == '__main__':
    dm = Dmsetup()
    dm.snapshot('origin', '/dev/loop1', 'snapshot', '/dev/loop0')
    print dm.get_table('origin')
    print dm.get_table('snapshot')
