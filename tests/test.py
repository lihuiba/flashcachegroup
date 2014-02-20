#!/usr/bin/env python

import sys
sys.path.append('..')

from libfcg.fcg import FCG

if __name__ == '__main__':
	fcg = FCG()
	fcg.create_group('tfcg', ['/dev/loop3'], '4k', 'back')
