#!/usr/bin/env python

import sys
sys.path.append('..')

from libfcg.fcg import FCG

if __name__ == '__main__':
	hdd1 = '/dev/loop0'
	hdd2 = '/dev/loop1'
	hdd3 = '/dev/loop2'
	ssd = '/dev/loop3'
	fcg = FCG('tfcg')
	fcg.create_group([ssd], '4k', 'back')
	#fcg.delete_group()
	fcg.add_disk(hdd1)
	#fcg.rm_disk(hdd1)
	fcg.add_disk(hdd2)
	fcg.add_disk(hdd3)
	fcg.rm_disk(hdd1)
	fcg.rm_disk(hdd3)
	fcg.add_disk(hdd3)
	fcg.add_disk(hdd1)
