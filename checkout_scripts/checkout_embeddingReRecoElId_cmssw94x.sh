#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc630
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh

scram project CMSSW_9_4_4
cd CMSSW_9_4_4/src
cmsenv

git cms-init
git cms-addpkg TauAnalysis/MCEmbeddingTools
git cms-merge-topic perahrens:embeddingReRecoElId_cmssw94x

#add additional packages of Generator and Geant to handle gc bug
for pkg in $(ls /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/CMSSW_9_4_2/src/GeneratorInterface/); do
  git cms-addpkg GeneratorInterface/$pkg
done

for pkg in $(ls /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/CMSSW_9_4_2/src/SimG4CMS/); do
  git cms-addpkg SimG4CMS/$pkg
done

for pkg in $(ls /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/CMSSW_9_4_2/src/SimG4Core/); do
  git cms-addpkg SimG4Core/$pkg
done

scramv1 b -j12

git clone https://github.com/janekbechtel/grid-control
git clone https://github.com/perahrens/gc_configs_for_embedding.git
