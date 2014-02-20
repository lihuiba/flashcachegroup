#!/usr/bin/env python

import sys
sys.path.append('..')

from libfcg.fcg import FCG

if __name__ == '__main__':
	fcg = FCG('tfcg')
	fcg.create_group(['/dev/loop3'], '4k', 'back')
	#fcg.delete_group()
	fcg.add_disk('/dev/loop1')
	fcg.rm_disk('/dev/loop1')
