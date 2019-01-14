# gc_configs_for_embedding

This package collects the configs (cmsRun, gridcontroll, inputs dbs files) for embedding, such that one can starts a large scale production

## 2018 


export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh

scram project CMSSW_10_2_0

cd CMSSW_10_2_0/src

cmsenv

git cms-init

git cms-addpkg TauAnalysis/MCEmbeddingTools

git cms-merge-topic KIT-CMS:embedding_from-CMSSW_10_2_0

scramv1 b -j 12

git clone https://github.com/janekbechtel/grid-control

git clone https://github.com/KIT-CMS/gc_configs_for_embedding.git

cd gc_configs_for_embedding

python Prepare_DATA_2018_CMSSW1020.py


## 2017

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

git clone https://github.com/KIT-CMS/gc_configs_for_embedding.git

cd gc_configs_for_embedding

python Prepare_DATA_2017_CMSSW944.py


## 2016

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh

cmsrel CMSSW_8_0_26_patch1

cd CMSSW_8_0_26_patch1/src

cmsenv

git cms-merge-topic swayand:fixingforembedding_cmss8026p1

scramv1 b -j12

git clone https://github.com/janekbechtel/grid-control

git clone https://github.com/KIT-CMS/gc_configs_for_embedding.git

cd gc_configs_for_embedding

python Prepare_DATA_2016_CMSSW826.py
