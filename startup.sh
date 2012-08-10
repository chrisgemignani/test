#!/bin/bash
set -e
SCRIPT_DIR=$(dirname $0)
SERVICE_DIR=$(cd $SCRIPT_DIR && cd ./ && pwd)
LOGFILE=$SERVICE_DIR/var/log/gunicorn/hello.log
LOGDIR=$(dirname $LOGFILE)

NUM_WORKERS=3
# user/group to run as
USER=ubuntu
GROUP=ubuntu
cd $SERVICE_DIR/hello
source ../env/bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec ../env/bin/gunicorn_django -w $NUM_WORKERS \
    --user=$USER --group=$GROUP --log-level=debug \
    --log-file=$LOGFILE 2>>$LOGFILE -b 0.0.0.0:8000
