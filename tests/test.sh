#!/bin/sh
for i in `seq 1 10`
do
    echo "----------$i----------" 
    echo "----------$i----------" >> test.log
    ./single_test.sh >> test.log
done
