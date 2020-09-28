
#source "$GC_LANDINGZONE/gc-run.lib" || exit 101
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
scram project CMSSW_10_6_12
cd CMSSW_10_6_12/src
cmsenv
tar xvfz cmssw_${ERA}.tar.gz
eval $(scram runtime -sh)
cd -

cmsRun selection.py
cmsRun lheprodandcleaning.py
cmsRun generator_preHLT.py

scram project CMSSW_10_2_16_UL
cd CMSSW_10_2_16_UL/src
cmsenv
tar xvfz cmssw_${ERA}_hlt.tar.gz
eval $(scram runtime -sh)
cd -

cmsRun generator_HLT.py
cd CMSSW_10_6_12/src
cmsenv
eval $(scram runtime -sh)
cd -

cmsRun generator_postHLT.py
cmsRun merging.py