#!/bin/sh
work_dir="/root/flashcachegroup"
log_file="/root/flashcachegroup/tests/test.log"
ssd="/dev/loop1"
hdd1="/dev/loop2"
hdd2="/dev/loop3"
bak_hdd1="/root/bak-hdd1"
bak_hdd2="/root/bak-hdd2"
cache_hdd1="/dev/mapper/cache_loop2"
cache_hdd2="/dev/mapper/cache_loop3"
echo "Test start at time: "
echo `date`
echo "If cmp diff occurs in log, then test failed..."
cd ..
python fcg-create.py -g testgroup -c $ssd
echo "Test 1:"
python fcg-add.py -g testgroup -h $hdd1
python fcg-add.py -g testgroup -h $hdd2
cmp $bak_hdd1 $cache_hdd1
cmp $bak_hdd2 $cache_hdd2
echo "Test 2:"
python fcg-remove.py -g testgroup -h $hdd1
cmp $bak_hdd2 $cache_hdd2
python fcg-add.py -g testgroup -h $hdd1
cmp $bak_hdd1 $cache_hdd1
cmp $bak_hdd2 $cache_hdd2
python fcg-remove.py -g testgroup -h $hdd2
cmp $bak_hdd1 $cache_hdd1
python fcg-add.py -g testgroup -h $hdd2
cmp $bak_hdd1 $cache_hdd1
cmp $bak_hdd2 $cache_hdd2
echo "Test 3:"
python fcg-remove.py -g testgroup -h $hdd2
python fcg-remove.py -g testgroup -h $hdd1

python fcg-add.py -g testgroup -h $hdd2
python fcg-add.py -g testgroup -h $hdd1

cmp $bak_hdd1 $cache_hdd1
cmp $bak_hdd2 $cache_hdd2
python fcg-delete.py -g testgroup
