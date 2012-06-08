#! /bin/bash
COUNTER=2
for line in `cat meshrouters.txt`; do
	./parallel_wsn.py -H $line "set_addr 10.$COUNTER"
	COUNTER=$((COUNTER+1))
done
