#!/usr/bin/env python

from common import executor
from common import processutils as putils

class Dmsetup(executor.Executor):
	def __init__(self, execute=putils.execute):
		super(Dmsetup, self).__init__(root_helper='', execute=execute)

	def _run(self, *args, **kwargs):
		self._execute(self._cmd, *args, run_as_root=True, **kwargs)

	def _run_dmsetup(self, dmsetup_command, *args):
		(out, err) = self._execute('dmsetup', dmsetup_command, *args,
									run_as_root=True,
									root_helper=self._root_helper)
		return (out, err)

	def create_table(self, name, table):
		self._run_dmsetup('create', name, table)

	def delete_table(self):
		pass

	def reload_table(self):
		pass

	def get_table(self):
		(out, ret) = self._run_dmsetup('table')
		return out

if __name__ == '__main__':
	dm = Dmsetup()
	print dm.get_table()
