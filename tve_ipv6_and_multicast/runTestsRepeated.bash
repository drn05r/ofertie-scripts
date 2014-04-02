#!/bin/bash
d=`dirname $0`
basedir=`cd ${d}; pwd`
#sudo `which python` ${basedir}/$1
#sleep 10
#sudo `which python` ${basedir}/$1
for ((i=1; i<=$2; i++)); do
	echo "===== Iteration: $i ====="
	sudo `which python` ${basedir}/$1
	if $i -ne $2; then
		sleep 30
	fi
done
