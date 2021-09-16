#!/bin/bash
set -e

CMSSW_MAIN=$1
CMSSW_HLT=$2
INPUTFILE=$3
STARTTASK=$4
NTHREADS=$5
echo "Running preselection"
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
echo "setting up main cmssw"
(

    cd ${CMSSW_MAIN}/src
    eval $(scram runtime -sh)
    cd -
    cmsRun -n $NTHREADS preselection.py
)
echo " --------------"
echo " Finished Production !"