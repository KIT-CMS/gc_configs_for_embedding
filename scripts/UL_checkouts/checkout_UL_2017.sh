#!/bin/bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
scram project CMSSW_10_6_28
cd CMSSW_10_6_28/src
eval `scramv1 runtime -sh`

git cms-init
git cms-addpkg TauAnalysis/MCEmbeddingTools
git cms-addpkg SimG4CMS
git cms-addpkg SimG4Core
git cms-merge-topic KIT-CMS:embedding_UL_10_6_28

scramv1 b -j 12

# git clone git@github.com:KIT-CMS/grid-control.git
# git clone git@github.com:KIT-CMS/gc_configs_for_embedding.git
# cd gc_configs_for_embedding
