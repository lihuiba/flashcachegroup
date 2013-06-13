#!/bin/sh
for i in `seq 1 2`
do
    echo "----------$i----------" >> test.log
    ./single_test.sh >> test.log
done
