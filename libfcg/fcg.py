#!/usr/bin/env python


from flashcachegroup.libfcg.common import executor

class FCG(executor.Executor):
	def __init__(self, cmd, root_helper, execute):
		super(FCG, self).__init__(root_helper, execute=execute)
		self._cmd = cmd

	def _run(self, *args, **kwargs):
		self._execute(self._cmd, *args, run_as_root=True, **kwargs)

	def create_group(self):
		pass

	def add_disk(self):
		pass

	def rm_disk(self):
		pass

	def delete_group(self):
		pass
