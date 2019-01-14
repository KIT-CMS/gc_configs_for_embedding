# gc_configs_for_embedding

This package collects the configs (cmsRun, gridcontroll, inputs dbs files) for embedding, such that one can starts a large scale production


e.g.

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh

scram project CMSSW_9_4_4

cd CMSSW_9_4_4/src

cmsenv

git cms-init

git cms-addpkg TauAnalysis/MCEmbeddingTools

git cms-merge-topic perahrens:embeddingReRecoElId_cmssw94x

scramv1 b -j 12

git clone https://github.com/janekbechtel/grid-control

git clone https://github.com/perahrens/gc_configs_for_embedding.git
