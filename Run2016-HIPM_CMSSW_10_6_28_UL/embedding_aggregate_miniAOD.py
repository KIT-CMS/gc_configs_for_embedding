# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: SKIM -s NONE --filein file:merged.root --fileout file:merged_large.root --era Run2_2018 --data --scenario pp --conditions 123X_dataRun2_v2 --eventcontent MINIAODSIM --datatier USER --customise_commands process.MINIAODSIMoutput.outputCommands = cms.untracked.vstring("keep *") -n -1 --no_exec --python_filename=aggregation.py
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2016_HIPM_cff import Run2_2016_HIPM

process = cms.Process("NONE", Run2_2016_HIPM)

# import of standard configurations
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.EventContent.EventContent_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

# Input source
process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring("file:merged.root"),
    secondaryFileNames=cms.untracked.vstring(),
)

process.options = cms.untracked.PSet()

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation=cms.untracked.string("SKIM nevts:-1"),
    name=cms.untracked.string("Applications"),
    version=cms.untracked.string("$Revision: 1.19 $"),
)

# Output definition

process.MINIAODSIMoutput = cms.OutputModule(
    "PoolOutputModule",
    compressionAlgorithm=cms.untracked.string("LZMA"),
    compressionLevel=cms.untracked.int32(4),
    dataset=cms.untracked.PSet(
        dataTier=cms.untracked.string("USER"), filterName=cms.untracked.string("")
    ),
    dropMetaData=cms.untracked.string("ALL"),
    eventAutoFlushCompressedSize=cms.untracked.int32(-900),
    fastCloning=cms.untracked.bool(False),
    fileName=cms.untracked.string("file:merged_large.root"),
    outputCommands=process.MINIAODSIMEventContent.outputCommands,
    overrideBranchesSplitLevel=cms.untracked.VPSet(
        cms.untracked.PSet(
            branch=cms.untracked.string("patPackedCandidates_packedPFCandidates__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string("recoGenParticles_prunedGenParticles__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string(
                "patTriggerObjectStandAlones_slimmedPatTrigger__*"
            ),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string("patPackedGenParticles_packedGenParticles__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string("patJets_slimmedJets__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string("recoVertexs_offlineSlimmedPrimaryVertices__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string(
                "recoCaloClusters_reducedEgamma_reducedESClusters_*"
            ),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string(
                "EcalRecHitsSorted_reducedEgamma_reducedEBRecHits_*"
            ),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string(
                "EcalRecHitsSorted_reducedEgamma_reducedEERecHits_*"
            ),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string("recoGenJets_slimmedGenJets__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string("patJets_slimmedJetsPuppi__*"),
            splitLevel=cms.untracked.int32(99),
        ),
        cms.untracked.PSet(
            branch=cms.untracked.string(
                "EcalRecHitsSorted_reducedEgamma_reducedESRecHits_*"
            ),
            splitLevel=cms.untracked.int32(99),
        ),
    ),
    overrideInputFileSplitLevels=cms.untracked.bool(True),
    splitLevel=cms.untracked.int32(0),
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, "106X_dataRun2_v35", "")

# Path and EndPath definitions
process.MINIAODSIMoutput_step = cms.EndPath(process.MINIAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.MINIAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask

associatePatAlgosToolsTask(process)


# Customisation from command line

process.MINIAODSIMoutput.outputCommands = cms.untracked.vstring("keep *")
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete

process = customiseEarlyDelete(process)
# End adding early deletion
