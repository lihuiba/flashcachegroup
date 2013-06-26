#!/bin/sh
for i in `seq 1 365`
do
    echo "----------$i----------" 
    echo "----------$i----------" >> log
    ./single_test.sh >> log
done
