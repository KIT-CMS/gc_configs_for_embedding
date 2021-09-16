#!/bin/bash
set -e
export XRD_LOGLEVEL="Info"
echo " --------------"
echo "Job Parameter Set: "
echo "TARBALL_PATH: ${TARBALL_PATH}"
echo "CMSSW_MAIN: ${CMSSW_MAIN}"
echo "CMSSW_HLT: ${CMSSW_HLT}"
echo "FILENUMBER: ${FILENUMBER}"
echo "INPUTPATH: ${INPUTPATH}"
echo "Set input file path .."

FOLDER=$(($FILENUMBER%100))
FOLDER=$(($FOLDER+1))
export INPUTFILE=$INPUTPATH/$FOLDER/PreRAWskimmed_$FILENUMBER.root

echo $INPUTFILE

echo "frist copy the two tarballs"
gfal-copy ${TARBALL_PATH}/cmssw_${CMSSW_MAIN}.tar.gz .
gfal-copy ${TARBALL_PATH}/cmssw_${CMSSW_HLT}.tar.gz .

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

(
    echo "setting up main cmssw"
    scram project ${CMSSW_MAIN}
    tar -xf cmssw_${CMSSW_MAIN}.tar.gz
    rm cmssw_${CMSSW_MAIN}.tar.gz
    cd ${CMSSW_MAIN}/src
    eval $(scram runtime -sh)
    cd -
    cmsRun selection.py $INPUTFILE
    cmsRun lheprodandcleaning.py
    cmsRun generator_preHLT.py
)

echo "now switchting CMSSW for HLT step"

(
    eval $(scram unsetenv -sh)
    scram project ${CMSSW_HLT}
    tar -xf cmssw_${CMSSW_HLT}.tar.gz
    rm cmssw_${CMSSW_HLT}.tar.gz
    cd ${CMSSW_HLT}/src
    eval $(scram runtime -sh)
    cd -
    cmsRun generator_HLT.py
)

echo "now switchting back to main CMSSW for merging"

(
    eval $(scram unsetenv -sh)
    cd ${CMSSW_MAIN}/src
    eval $(scram runtime -sh)
    cd -
    cmsRun generator_postHLT.py
    cmsRun merging.py
)
echo " --------------"
echo " Finished Production !"