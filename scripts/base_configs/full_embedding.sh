#!/bin/bash
set -e
export XRD_LOGLEVEL="Info"
echo " --------------"

echo "frist copy the two tarballs"
gfal-copy ${TARBALL_PATH}/cmssw_${CMSSW_MAIN}.tar.gz .
gfal-copy ${TARBALL_PATH}/cmssw_${CMSSW_HLT}.tar.gz .
echo "setting up main cmssw"
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
scram project ${CMSSW_MAIN}
tar -xf cmssw_${CMSSW_MAIN}.tar.gz
rm cmssw_${CMSSW_MAIN}.tar.gz
cd ${CMSSW_MAIN}/src
eval $(scram runtime -sh)
cd -

cmsRun selection.py
cmsRun lheprodandcleaning.py
cmsRun generator_preHLT.py

echo "now switchting CMSSW for HLT step"
scram project ${CMSSW_HLT}
tar -xf cmssw_${CMSSW_HLT}.tar.gz
cd ${CMSSW_HLT}/src
eval $(scram runtime -sh)
cd -

cmsRun generator_HLT.py

echo "now switchting back to main CMSSW for merging"
cd ${CMSSW_MAIN}/src
eval $(scram runtime -sh)
cd -


cmsRun generator_postHLT.py
cmsRun merging.py
echo " --------------"
echo " Finished Production !"
echo "Write output file ...."