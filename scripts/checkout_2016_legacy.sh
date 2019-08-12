export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# needed for selection -> cleaning -> simulation -> merging into AODSIM
scram project CMSSW_8_0_33

#first setup the 8_0_33 env
cd CMSSW_8_0_33/src
cmsenv
git cms-merge-topic KIT-CMS:emb_2016_legacy
git cms-addpkg SimG4CMS
git cms-addpkg SimG4Core
scramv1 b -j 12

git clone git@github.com:KIT-CMS/grid-control.git
git clone git@github.com:KIT-CMS/gc_configs_for_embedding.git

cd gc_configs_for_embedding
python Prepare_DATA_2016_CMSSW8033.py

# and now the 9_4_14 env
cd ../../../

# needed for AODSIM -> MINIAODSIM
scram project CMSSW_9_4_14
cd CMSSW_9_4_14/src

cmsenv
git cms-merge-topic KIT-CMS:emb_2016_legacy_94x
scramv1 b -j 12

git clone git@github.com:KIT-CMS/grid-control.git
git clone git@github.com:KIT-CMS/gc_configs_for_embedding.git

cd gc_configs_for_embedding
python Prepare_DATA_2016_CMSSW9414_MiniAOD.py
