#!/bin/bash

LOG_FILE='killout.txt'
ERR_FILE='stderror.err'
STATUS_LINES=15
POLL_RATE=2

run_ktools_kill(){
     FMCALC=`ps -C fmcalc -o pmem | grep -v MEM | sort -n -r | head -1`
     GULCALC=`ps -C gulcalc -o pmem | grep -v MEM | sort -n -r | head -1`
     GETMODEL=`ps -C getmodel -o pmem | grep -v MEM | sort -n -r | head -1`
     echo "TOTALS:  $FMCALC $GULCALC $GETMODEL" > killout.txt
     free -h > zzfree
     ps -aux | grep fmcalc > zzfmcalc
     ps -aux | grep gulcalc > zzgulcalc
     echo "**************** DOING KILL ***************"
     echo "$(date +"%T"): killing eve" >> killout.txt
     pkill -9 eve
     echo "$(date +"%T"): killing getmodel" >> killout.txt
     pkill -9 getmodel
     echo "$(date +"%T"): killing gulcalc" >> killout.txt
     pkill -9 gulcalc
     echo "$(date +"%T"): killing fmcalc" >> killout.txt
     pkill -9 fmcalc
     echo "$(date +"%T"): killing summarycalc" >> killout.txt
     pkill -9 summarycalc
     echo "$(date +"T"): kill done" >> killout.txt
     sleep 2
     ps -aux | grep fmcalc > zzfmcalc1
     ps -aux | grep gulcalc > zzgulcalc1
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
