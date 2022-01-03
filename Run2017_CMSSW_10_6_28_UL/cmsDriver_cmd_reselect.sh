###### cmsDriver.py commands for embedding in CMSSW_10_6_28 ######
## from https://twiki.cern.ch/twiki/bin/view/CMS/PdmVLegacy2017Analysis
#### Embedding on Data

### Step 0: Preselection from DoubleMuon

cmsDriver.py RECO -s RAW2DIGI,L1Reco,RECO,PAT --runUnscheduled \
--data --scenario pp --conditions 106X_dataRun2_v35 \
--era Run2_2017 \
--eventcontent RAW --datatier RAW \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run2_2017,\
TauAnalysis/MCEmbeddingTools/customisers.customiseSelecting \
--filein file:D671E4CB-B468-E811-B0BA-FA163EFF1C10.root  \
--fileout PreRAWskimmed.root -n -1 --no_exec --python_filename=preselection.py

### Step 1: Selection of Z->MuMu
cmsDriver.py RECO -s RAW2DIGI,L1Reco,RECO,PAT --runUnscheduled \
--data --scenario pp --conditions 106X_dataRun2_v35 \
--era Run2_2017 \
--eventcontent RAWRECO --datatier RAWRECO \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run2_2017,\
TauAnalysis/MCEmbeddingTools/customisers.customiseSelecting_Reselect \
--filein file:PreRAWskimmed.root  \
--fileout RAWskimmed.root -n -1 --no_exec --python_filename=selection.py

### Step 2: Cleaning and preparation for simulation (saving LHE products)
cmsDriver.py LHEprodandCLEAN --filein file:RAWskimmed.root \
--fileout file:lhe_and_cleaned.root --runUnscheduled --data --era Run2_2017 \
--scenario pp --conditions 106X_dataRun2_v35 --eventcontent RAWRECO \
--datatier RAWRECO --step RAW2DIGI,RECO,PAT \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run2_2017,\
TauAnalysis/MCEmbeddingTools/customisers.customiseLHEandCleaning_Reselect \
--no_exec -n -1 --python_filename lheprodandcleaning.py

### Step 3: Simulation of the hard process
cmsDriver.py TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py \
--filein file:lhe_and_cleaned.root --fileout simulated_and_cleaned_preHLT.root \
--conditions 106X_mc2017_realistic_v6 --era Run2_2017 \
--eventcontent RAWSIM --step GEN,SIM,DIGI,L1,DIGI2RAW \
--datatier RAWSIM --customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseGenerator_preHLT_Reselect \
--beamspot Realistic25ns13TeVEarly2017Collision --no_exec -n -1 --python_filename generator_preHLT.py \
--geometry DB:Extended --mc

cmsDriver.py TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py \
--filein file:simulated_and_cleaned_preHLT.root --fileout simulated_and_cleaned_posthlt.root \
--conditions 94X_mc2017_realistic_v15 --era Run2_2017 \
--eventcontent RAWSIM --step HLT:2e34v40 \
--datatier RAWSIM \
--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
--customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseGenerator_HLT_Reselect \
--beamspot Realistic25ns13TeVEarly2017Collision --no_exec -n -1 --python_filename generator_HLT.py \
--geometry DB:Extended --mc

cmsDriver.py TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py \
--filein file:simulated_and_cleaned_posthlt.root --fileout simulated_and_cleaned.root \
--conditions 106X_mc2017_realistic_v6 --era Run2_2017 \
--eventcontent RAWRECO --step RAW2DIGI,RECO \
--datatier RAWRECO --customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseGenerator_postHLT_Reselect \
--beamspot Realistic25ns13TeVEarly2017Collision --no_exec -n -1 --python_filename generator_postHLT.py \
--geometry DB:Extended --mc

### Step 4: Merging of simulated hard process and cleaned data:
cmsDriver.py PAT -s PAT \
--filein file:simulated_and_cleaned.root  \
--fileout file:merged.root --era Run2_2017 \
--runUnscheduled --data --scenario pp --conditions 106X_dataRun2_v35 \
--eventcontent  MINIAODSIM --datatier USER \
--customise \
TauAnalysis/MCEmbeddingTools/customisers.customiseMerging_Reselect \
--customise_commands 'process.patTrigger.processName = cms.string("SIMembeddingHLT") \nprocess.slimmedPatTrigger.triggerResults =  cms.InputTag("TriggerResults::SIMembeddingHLT") \nprocess.patMuons.triggerResults =  cms.InputTag("TriggerResults::SIMembeddingHLT")' \
-n -1 --no_exec --python_filename=merging.py

### NanoAOD Setp

cmsDriver.py  -s NANO \
--data --eventcontent NANOAOD --datatier NANOAOD \
--no_exec --conditions 106X_dataRun2_v35 \
--era Run2_2017 \
--filein file:test_17.root \
--fileout file:merged_nano.root \
--python_filename=embedding_nanoaod.py \
--customise TauAnalysis/MCEmbeddingTools/customisers.customiseNanoAOD \
--customise_commands 'process.unpackedPatTrigger.triggerResults = cms.InputTag("TriggerResults::SIMembeddingHLT") \nprocess.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_SIMembeddingHLT")  # Trigger information \nprocess.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_MERGE")  # MET filter flags'
# after set nanoaod path manually to:
# process.nanoAOD_step = cms.Path(process.genParticleSequence + process.nanoSequenceCommon + process.nanoSequenceOnlyFullSim + process.muonMC + process.electronMC + process.photonMC + process.tauMC + process.globalTablesMC + process.btagWeightTable + process.genWeightsTable + process.genParticleTables)