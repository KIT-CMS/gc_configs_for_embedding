# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: -s NANO --data --eventcontent NANOAOD --datatier NANOAOD --no_exec --conditions 106X_dataRun2_v35 --era Run2_2017 --filein file:test_17.root --fileout file:test_nano_17.root --python_filename=embedding_nanoaod.py --customise TauAnalysis/MCEmbeddingTools/customisers.customiseNanoAOD --customise_commands process.unpackedPatTrigger.triggerResults = cms.InputTag("TriggerResults::SIMembeddingHLT") \nprocess.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_SIMembeddingHLT")  # Trigger information \nprocess.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_MERGE")  # MET filter flags
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2017_cff import Run2_2017

process = cms.Process('NANO',Run2_2017)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:test_17.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('-s nevts:1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:merged_nano.root'),
    outputCommands = process.NANOAODEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v35', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.mergedGenParticles + process.genParticles2HepMC + process.genParticleSequence + process.nanoSequenceCommon + process.nanoSequenceOnlyFullSim + process.muonMC + process.electronMC + process.photonMC + process.tauMC + process.globalTablesMC + process.btagWeightTable + process.genWeightsTable + process.genParticleTables)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeData 

#call to customisation function nanoAOD_customizeData imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeData(process)

# Automatic addition of the customisation function from TauAnalysis.MCEmbeddingTools.customisers
from TauAnalysis.MCEmbeddingTools.customisers import customiseNanoAOD 

#call to customisation function customiseNanoAOD imported from TauAnalysis.MCEmbeddingTools.customisers
process = customiseNanoAOD(process)

process.unpackedPatTrigger.triggerResults = cms.InputTag('TriggerResults::SIMembeddingHLT')

process.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_SIMembeddingHLT")  # Trigger information
process.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_MERGE")  # MET filter flags
process.NANOAODoutput.outputCommands.remove("keep edmTriggerResults_*_*_*")
process.genParticles2HepMC.genEventInfo = cms.InputTag("generator", "", "SIMembeddingpreHLT")
# update the PUPPIMET collection
suffix = "RERUNPUPPI"
# suffix = "MERGE"
process.patJetsReapplyJECPuppi.jetSource = cms.InputTag("slimmedJetsPuppi", "", "MERGE")
process.patJetCorrFactorsReapplyJECPuppi.src = cms.InputTag("slimmedJetsPuppi", "", "MERGE")
process.puppiMetTable.src = cms.InputTag("slimmedMETsPuppi", "", "RERUNPUPPI")
process.rawPuppiMetTable.src = cms.InputTag("slimmedMETsPuppi", "", "RERUNPUPPI")
process.slimmedMETsPuppi.t01Variation = cms.InputTag("slimmedMETsPuppi", "", "RERUNPUPPI")
process.metrawCaloPuppi.metSource = cms.InputTag("slimmedMETsPuppi", "", "RERUNPUPPI")
process.pfMetPuppi.metSource = cms.InputTag("slimmedMETsPuppi", "", "RERUNPUPPI")

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
