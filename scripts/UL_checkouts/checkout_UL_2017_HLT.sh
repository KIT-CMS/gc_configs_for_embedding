#!/bin/bash
if [ ! -d "CMSSW_9_4_14_UL_patch1" ]; then
    export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
    source $VO_CMS_SW_DIR/cmsset_default.sh
    scram project CMSSW_9_4_14_UL_patch1
    cd CMSSW_9_4_14_UL_patch1/src
    eval `scramv1 runtime -sh`

    git cms-init
    git cms-addpkg TauAnalysis/MCEmbeddingTools
    git cms-addpkg SimG4CMS
    git cms-addpkg SimG4Core
    git cms-merge-topic KIT-CMS:embedding_UL_9_4_14_UL_patch1

    scramv1 b -j 12
fi
