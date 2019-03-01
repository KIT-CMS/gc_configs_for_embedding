export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh

scram project CMSSW_10_2_4_patch1
# for Run2018D use
# scram project CMSSW_10_2_5_patch1

cd CMSSW_10_2_4_patch1/src
# for Run2018D use
# cd CMSSW_10_2_5_patch1/src

cmsenv

git cms-init

git cms-addpkg TauAnalysis/MCEmbeddingTools

git cms-addpkg SimG4CMS

git cms-addpkg SimG4Core

git cms-merge-topic KIT-CMS:embedding_from-CMSSW_10_2_0

scramv1 b -j 12

git clone git@github.com:KIT-CMS/grid-control.git

git clone git@github.com:KIT-CMS/gc_configs_for_embedding.git

cd gc_configs_for_embedding
