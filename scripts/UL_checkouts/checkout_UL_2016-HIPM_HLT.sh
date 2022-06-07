#!/bin/bash
if [ ! -d "CMSSW_8_0_33_UL" ]; then
    export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
    source $VO_CMS_SW_DIR/cmsset_default.sh
    scram project CMSSW_8_0_33_UL
    cd CMSSW_8_0_33_UL/src
    eval `scramv1 runtime -sh`

    git cms-init
    git cms-addpkg TauAnalysis/MCEmbeddingTools
    git cms-addpkg SimG4CMS
    git cms-addpkg SimG4Core
    git cms-merge-topic KIT-CMS:embedding_UL_8_0_33_UL

    scramv1 b -j 12
fi
