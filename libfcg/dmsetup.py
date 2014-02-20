#!/usr/bin/env python

import os
from common import executor
from common import processutils as putils
import utils
import dmtable

mapdev_prefix = '/dev/mapper/'

class Dmsetup(executor.Executor):
	def __init__(self, execute=putils.execute):
		super(Dmsetup, self).__init__(root_helper='', execute=execute)

	def _run_dmsetup(self, dmsetup_command, *args):
		(out, err) = self._execute('dmsetup', dmsetup_command, *args,
									run_as_root=True)
		out = out.strip()
		return (out, err)

	def create_table(self, name, table):
		table_file = utils.write2tempfile(table)
		self._run_dmsetup('create', name, table_file)
		return mapdev_prefix + name

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

if __name__ == '__main__':
	dm = Dmsetup()
	print dm.show_table()
	print dm.get_table('uvm--vg-root')
