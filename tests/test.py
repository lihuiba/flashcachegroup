#!/usr/bin/env python

import time
import sys
sys.path.append('..')

from libfcg.fcg import FCG

def run_time(func, *args, **kwargs):
    t0 = time.time()
    func(*args, **kwargs)
    t1 = time.time()
    print '%d s, %s'%(t1-t0, func)

if __name__ == '__main__':
    hdd1 = '/dev/loop0'
    hdd2 = '/dev/loop1'
    hdd3 = '/dev/loop2'
    ssd = '/dev/loop3'
    fcg = FCG('tfcg')
    run_time(fcg.create_group, [ssd], '4k', 'back')
    run_time(fcg.add_disk, hdd1)
    run_time(fcg.add_disk, hdd1)
    run_time(fcg.add_disk, hdd2)
    run_time(fcg.add_disk, hdd2)
    run_time(fcg.add_disk, hdd2)
    run_time(fcg.add_disk, hdd2)
    run_time(fcg.add_disk, hdd3)
    run_time(fcg.rm_disk, hdd1)
    run_time(fcg.rm_disk, hdd3)
    run_time(fcg.add_disk, hdd3)
    run_time(fcg.add_disk, hdd1)
    run_time(fcg.rm_disk, hdd1)
    run_time(fcg.rm_disk, hdd2)
    run_time(fcg.rm_disk, hdd3)
    run_time(fcg.delete_group)
