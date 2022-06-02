# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py --filein file:simulated_and_cleaned_preHLT.root --fileout simulated_and_cleaned_posthlt.root --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 --era Run2_2016 --eventcontent RAWSIM --step HLT:25ns15e33_v4 --datatier RAWSIM --customise_commands process.source.bypassVersionCheck = cms.untracked.bool(True) --customise TauAnalysis/MCEmbeddingTools/customisers.customiseGenerator_HLT_Reselect --beamspot Realistic25ns13TeV2016Collision --no_exec -n -1 --python_filename generator_HLT_v2.py --geometry DB:Extended --mc
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

# In order to reduce diskusage of job, remove output of lheprodandcleaning.py --> lhe_and_cleaned.root
import os

if os.path.exists("lhe_and_cleaned.root"):
    os.remove("lhe_and_cleaned.root")

process = cms.Process("HLTEMB", eras.Run2_2016)

# import of standard configurations
process.load("Configuration.StandardSequences.Services_cff")
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.EventContent.EventContent_cff")
process.load("SimGeneral.MixingModule.mixNoPU_cfi")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("HLTrigger.Configuration.HLT_25ns15e33_v4_cff")
process.load("Configuration.StandardSequences.EndOfProcess_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

# Input source
process.source = cms.Source(
    "PoolSource",
    dropDescendantsOfDroppedBranches=cms.untracked.bool(False),
    fileNames = cms.untracked.vstring("file:/ceph/sbrommer/embedding/UL/studies/2016_F_v2/simulated_and_cleaned_preHLT.root"),
    secondaryFileNames=cms.untracked.vstring(),
    inputCommands=cms.untracked.vstring(
        "keep *",
        "drop TotemTimingRecHitedmDetSetVector_totemTimingRecHits_*_*",
        "drop recoGsfElectrons_lowPtGsfElectrons_*_*",
        "drop floatedmValueMap_rekeyLowPtGsfElectronSeedValueMaps_*_*",
        "drop *_hpsPFTauDiscriminationByVVLooseIsolationMVArun2v1DBnewDMwLT_*_*",
        "drop TotemTimingDigiedmDetSetVector_totemTimingRawToDigi_*_*",
        "drop recoBeamSpot_onlineMetaDataDigis_*_*",
        "drop DCSRecord_onlineMetaDataDigis_*_*",
        "drop *_hpsPFTauDiscriminationByVVLooseIsolationMVArun2v1DBoldDMwLT_*_*",
        "drop *_lowPtGsfToTrackLinks_*_*",
        "drop *_hpsPFTauDiscriminationByVVLooseIsolationMVArun2v1DBdR03oldDMwLT_*_*",
        "drop recoGsfElectronCores_lowPtGsfElectronCores_*_*",
        "drop CTPPSRecord_onlineMetaDataDigis_*_*",
        "drop recoSuperClusters_lowPtGsfElectronSuperClusters_*_*",
        "drop CTPPSPixelDataErroredmDetSetVector_ctppsPixelDigis_*_*",
        "drop *_gsfTracksOpenConversions_*_*",
        "drop floatedmValueMap_lowPtGsfElectronSeedValueMaps_*_*",
        "drop recoGsfTracks_lowPtGsfEleGsfTracks_*_*",
        "drop OnlineLuminosityRecord_onlineMetaDataDigis_*_*",
        "drop recoCaloClusters_lowPtGsfElectronSuperClusters_*_*",
        "drop floatedmValueMap_lowPtGsfElectronID_*_*",
        "drop CTPPSDiamondRecHitedmDetSetVector_ctppsDiamondRecHits_*_*",
        "drop *_inclusiveCandidateSecondaryVertices_*_*",
        "drop *_inclusiveCandidateSecondaryVerticesCvsL_*_*",
        "drop *_ctppsDiamondRawToDigi_*_*",
        "drop *_ctppsDiamondRecHits_*_*",
        "drop *_ctppsPixelClusters_*_*",
        "drop *_ctppsPixelDigis_*_*",
        "drop *_ctppsPixelDigis_*_*",
        "drop *_ctppsPixelLocalTracks_*_*",
        "drop *_ctppsPixelRecHits_*_*",
        "drop *_ctppsDiamondRawToDigi_*_*",
        "drop *_siPixelDigis_*_*",
        "drop *_tcdsDigis_*_*",
        "drop *_ak4PFJetsCHS_rho_LHEembeddingCLEAN",
    ),
)

process.options = cms.untracked.PSet()

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation=cms.untracked.string(
        "TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py nevts:-1"
    ),
    name=cms.untracked.string("Applications"),
    version=cms.untracked.string("$Revision: 1.19 $"),
)

# Output definition

process.RAWSIMoutput = cms.OutputModule(
    "PoolOutputModule",
    dataset=cms.untracked.PSet(
        dataTier=cms.untracked.string("RAWSIM"), filterName=cms.untracked.string("")
    ),
    eventAutoFlushCompressedSize=cms.untracked.int32(5242880),
    fileName=cms.untracked.string("simulated_and_cleaned_posthlt.root"),
    outputCommands=process.RAWSIMEventContent.outputCommands,
    splitLevel=cms.untracked.int32(0),
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(
    process.GlobalTag, "80X_mcRun2_asymptotic_2016_TrancheIV_v6", ""
)

# Path and EndPath definitions
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
process.schedule = cms.Schedule()
process.schedule.extend(process.HLTSchedule)
process.schedule.extend([process.endjob_step, process.RAWSIMoutput_step])

# customisation of the process.

# Automatic addition of the customisation function from TauAnalysis.MCEmbeddingTools.customisers
from TauAnalysis.MCEmbeddingTools.customisers import customiseGenerator_HLT_Reselect

# call to customisation function customiseGenerator_HLT_Reselect imported from TauAnalysis.MCEmbeddingTools.customisers
process = customiseGenerator_HLT_Reselect(process)

# Automatic addition of the customisation function from HLTrigger.Configuration.customizeHLTforMC
from HLTrigger.Configuration.customizeHLTforMC import customizeHLTforFullSim

# call to customisation function customizeHLTforFullSim imported from HLTrigger.Configuration.customizeHLTforMC
process = customizeHLTforFullSim(process)

# End of customisation functions

# Customisation from command line
process.source.bypassVersionCheck = cms.untracked.bool(True)
