#!/bin/sh

for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
do
    curl http://detection.default.svc.cluster.local/test_video/highway.mp4  &
    echo "Finish request"
done