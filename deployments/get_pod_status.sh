#!/bin/sh
status=`echo 1 | sudo -S kubectl get pod -n default -o wide | awk 'BEGIN {getline;getline;getline;getline;name=$1;status=$3;node=$7;print status}'`
echo $status
