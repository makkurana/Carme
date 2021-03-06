#!/bin/bash
# ----------------------------------------------
# Carme                                         
# ----------------------------------------------
# submitJob.sh - submit a slurm job                                                                                                                                                                     
# 
# usage: submitJob CARME_SLURM_SCRIPTS_PATH $DBJOBID $IMAGE $MOUNTS $NUM_GPUS_PER_NODE $MEM $NTASKS $WORKER_NODES JOBID IMAGE MOUNTS PARTITION NUM_GPUS_PER_NODE NUM_NODES JOB_NAME
#                                               
# see Carme development guide for documentation:
# * Carme/Carme-Doc/DevelDoc/CarmeDevelopmentDocu.md
#                                                   
# Copyright 2019 by Fraunhofer ITWM                 
# License: http://open-carme.org/LICENSE.md         
# Contact: info@open-carme.org                      
# ---------------------------------------------   

CARME_SCRIPTS_PATH=$1

LOGDIR="/home/$USER/.job-log-dir"
if [ ! -d $LOGDIR ]; then
    mkdir $LOGDIR
fi

DBJOBID=$2
IMAGE=$3
MOUNTS=$4
PARTITION=$5
NUM_GPUS_PER_NODE=$6
NUM_NODES=$7
JOB_NAME=$8
CARME_SCRIPT_PATH=$9
COUNTER=1
COUNTERLIMIT=1

echo "startJob" $JOB_NAME $NUM_NODES
#using tasks to get slurm to schedule not more jobs than the num of GPUs
CORES_PER_GPU=10
MEM_PER_GPU=30
NTASKS=$((CORES_PER_GPU*NUM_GPUS_PER_NODE))
WORKER_NODES=$((NUM_NODES-1))
MEM=$((MEM_PER_GPU*NUM_GPUS_PER_NODE))
while [ $COUNTER -le $COUNTERLIMIT ]
do
								if [ "$NUM_NODES" != 1 ]; then
																sbatch --partition=$PARTITION --job-name=$JOB_NAME --nodes=$NUM_NODES --ntasks-per-node=$NTASKS --mem=${MEM}G -o $LOGDIR/%j-$JOB_NAME.out -e $LOGDIR/%j-$JOB_NAME.err ${CARME_SCRIPTS_PATH}/slurm-parallel.sh $DBJOBID $IMAGE $MOUNTS $NUM_GPUS_PER_NODE $MEM $CARME_SCRIPT_PATH $NTASKS $WORKER_NODES 
								else
																sbatch  --partition=$PARTITION --job-name=$JOB_NAME --nodes=$NUM_NODES --ntasks-per-node=$NTASKS --mem=${MEM}G -o $LOGDIR/%j-$JOB_NAME.out -e $LOGDIR/%j-$JOB_NAME.err ${CARME_SCRIPTS_PATH}/slurm.sh $DBJOBID $IMAGE $MOUNTS $NUM_GPUS_PER_NODE $MEM $CARME_SCRIPT_PATH
								fi
        ((COUNTER++))
done

#--time=1440 # = 1 day
#--begin=now+180
printf "all jobs submitted\n"
