#!/bin/sh

for i in 1
do
    curl http://detection.default.svc.cluster.local/test_video/highway.mp4  &
    echo "Finish request"
done

# for i in 1 2 3 4 5 6 7 8 9
# do
#     curl http://hello.default.svc.cluster.local/  &
#     echo "Finish request"
# done