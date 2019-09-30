#!/bin/bash

LOG_FILE='killout.txt'
ERR_FILE='stderror.err'
STATUS_LINES=15
POLL_RATE=2

run_ktools_kill(){
    printf "\\n*** CPU LOAD *****************************" >> $LOG_FILE
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n $STATUS_LINES >> $LOG_FILE
    printf "\\n*** MEM LOAD *****************************"  >> $LOG_FILE
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n $STATUS_LINES >> $LOG_FILE

    echo "**************** output on STDERR killing run ***************" 
    echo "$(date +"%T"): about to kill " >> $LOG_FILE
    sleep 2
    pkill getmodel -9
    pkill gulcalc -9
    pkill fmcalc -9 
    echo "$(date +"%T"): kill done" >> $LOG_FILE
    exit 1
}

if hash inotifywait 2>/dev/null; then
    while inotifywait -e close_write $ERR_FILE; do
        if [ -s stderror.err ]; then
            run_ktools_kill
        fi
    done
else
    while : 
    do
        sleep $POLL_RATE
        if [ -s stderror.err ]; then
            run_ktools_kill
        fi
    done
fi
