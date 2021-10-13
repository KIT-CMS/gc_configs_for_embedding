###### cmsDriver.py commands for embedding in CMSSW_10_6_12 ######
## from https://twiki.cern.ch/twiki/bin/view/CMS/PdmVLegacy2018Analysis
#### Embedding on Data

### Step 0: Preselection from DoubleMuon

cmsDriver.py RECO -s RAW2DIGI,L1Reco,RECO,PAT --runUnscheduled \
--data --scenario pp --conditions 106X_dataRun2_v28 \
--era Run2_2018 \
--eventcontent RAW --datatier RAW \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run2_2018,\
TauAnalysis/MCEmbeddingTools/customisers.customiseSelecting \
--filein file:D671E4CB-B468-E811-B0BA-FA163EFF1C10.root  \
--fileout PreRAWskimmed.root -n -1 --no_exec --python_filename=preselection.py

### Step 1: Selection of Z->MuMu
cmsDriver.py RECO -s RAW2DIGI,L1Reco,RECO,PAT --runUnscheduled \
--data --scenario pp --conditions 106X_dataRun2_v28 \
--era Run2_2018 \
--eventcontent RAWRECO --datatier RAWRECO \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run2_2018,\
TauAnalysis/MCEmbeddingTools/customisers.customiseSelecting_Reselect \
--filein file:PreRAWskimmed.root  \
--fileout RAWskimmed.root -n -1 --no_exec --python_filename=selection.py

### Step 2: Cleaning and preparation for simulation (saving LHE products)
cmsDriver.py LHEprodandCLEAN --filein file:RAWskimmed.root \
--fileout file:lhe_and_cleaned.root --runUnscheduled --data --era Run2_2018 \
--scenario pp --conditions 106X_dataRun2_v28 --eventcontent RAWRECO \
--datatier RAWRECO --step RAW2DIGI,RECO,PAT \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run2_2018,\
TauAnalysis/MCEmbeddingTools/customisers.customiseLHEandCleaning_Reselect \
--no_exec -n -1 --python_filename lheprodandcleaning.py

### Step 3: Simulation of the hard process
cmsDriver.py TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py \
--filein file:lhe_and_cleaned.root --fileout simulated_and_cleaned_preHLT.root \
--conditions 106X_upgrade2018_realistic_v11_L1v1 --era Run2_2018 \
--eventcontent RAWRECO --step GEN,SIM,DIGI,L1,DIGI2RAW \
--datatier RAWSIM --customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseGenerator_Reselect \
--beamspot Realistic25ns13TeVEarly2018Collision --no_exec -n -1 --python_filename generator_preHLT.py \
--geometry DB:Extended --mc

cmsDriver.py TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py \
--filein file:simulated_and_cleaned_preHLT.root --fileout simulated_and_cleaned_posthlt.root \
--conditions 102X_upgrade2018_realistic_v15 --era Run2_2018 \
--eventcontent RAWSIM --step HLT:2018v32 \
--datatier RAWSIM \
--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
--beamspot Realistic25ns13TeVEarly2018Collision --no_exec -n -1 --python_filename generator_HLT.py \
--geometry DB:Extended --mc

cmsDriver.py TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py \
--filein file:simulated_and_cleaned_posthlt.root --fileout simulated_and_cleaned.root \
--conditions 106X_upgrade2018_realistic_v11_L1v1 --era Run2_2018 \
--eventcontent RAWSIM --step RAW2DIGI,RECO \
--datatier RAWRECO --customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseGenerator_Reselect \
--beamspot Realistic25ns13TeVEarly2018Collision --no_exec -n -1 --python_filename generator_postHLT.py \
--geometry DB:Extended --mc

### Step 4: Merging of simulated hard process and cleaned data:
cmsDriver.py PAT -s PAT \
--filein file:simulated_and_cleaned.root  \
--fileout file:merged.root --era Run2_2018 \
--runUnscheduled --data --scenario pp --conditions 106X_dataRun2_v28 \
--eventcontent  MINIAODSIM --datatier USER \
--customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseMerging_Reselect \
--customise_commands 'process.patTrigger.processName = cms.string("SIMembeddingHLT") \nprocess.slimmedPatTrigger.triggerResults =  cms.InputTag("TriggerResults::SIMembeddingHLT") \nprocess.patMuons.triggerResults =  cms.InputTag("TriggerResults::SIMembeddingHLT")' \
-n -1 --no_exec --python_filename=merging.py

### NanoAOD Setp

cmsDriver.py  -s NANO \
--data --eventcontent NANOAOD --datatier NANOAOD \
--no_exec --conditions 106X_dataRun2_v28 \
--era Run2_2018 \
--filein file:test_18.root \
--fileout file:test_nano_18.root \
--python_filename=embedding_nanoAOD.py
