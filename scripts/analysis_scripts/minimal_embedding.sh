#!/bin/bash
set -e

CMSSW_MAIN=$1
CMSSW_HLT=$2
INPUTFILE=$3
STARTTASK=$4
NTHREADS=$5
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
eval $(scram unsetenv -sh)
echo "Starting with task number $STARTTASK"
(
    echo "setting up main cmssw: "
    cd ${CMSSW_MAIN}/src
    eval $(scram runtime -sh)
    echo "$CMSSW_BASE"
    cd -
    if [ "$STARTTASK" -le 0 ]; then
        echo "Running task No. 0"
        cmsRun -n $NTHREADS selection.py
    fi
    if [ "$STARTTASK" -le 1 ]; then
        echo "Running task No. 1"
        cmsRun -n $NTHREADS lheprodandcleaning.py
    fi
    if [ "$STARTTASK" -le 2 ]; then
        echo "Running task No. 2"
        cmsRun -n $NTHREADS generator_preHLT.py
    fi
)
echo "now switchting CMSSW for HLT step"

(
    eval $(scram unsetenv -sh)
    cd ${CMSSW_HLT}/src
    eval $(scram runtime -sh)
    echo "$CMSSW_BASE"
    cd -
    if [ "$STARTTASK" -le 3 ]; then
        echo "Running task No. 3"
        cmsRun generator_HLT.py
    fi
)
echo "now switchting back to main CMSSW for merging"
(
    eval $(scram unsetenv -sh)
    cd ${CMSSW_MAIN}/src
    eval $(scram runtime -sh)
    echo "$CMSSW_BASE"
    cd -
    if [ "$STARTTASK" -le 4 ]; then
        echo "Running task No. 4"
        cmsRun -n $NTHREADS generator_postHLT.py
    fi
    if [ "$STARTTASK" -le 5 ]; then
        echo "Running task No. 5"
        cmsRun -n $NTHREADS merging.py
    fi
)
echo " --------------"
echo " Finished Production !"