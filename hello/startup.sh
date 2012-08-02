#!/bin/bash
set -e
LOGFILE=/var/log/gunicorn/hello.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
USER=ubuntu
GROUP=ubuntu
cd /home/ubuntu/test/hello
source ../bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec ../bin/gunicorn_django -w $NUM_WORKERS \
    --user=$USER --group=$GROUP --log-level=debug \
    --log-file=$LOGFILE 2>>$LOGFILE -b 0.0.0.0:8000