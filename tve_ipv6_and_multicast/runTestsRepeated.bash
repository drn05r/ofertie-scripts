#!/bin/bash
d=`dirname $0`
basedir=`cd ${d}; pwd`
for ((i=1; i<=$2; i++)); do
	sudo killall -9 iperf3
	echo "===== Iteration: $i ====="
	sudo `which python` ${basedir}/testsets/$1.py
	if [ $i -ne $2 ]; then
		sleep 30
	fi
done
