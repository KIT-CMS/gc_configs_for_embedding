# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: step0p5 --filein dbs:/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16DR80-FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/RAWAODSIM --mc --eventcontent RAWRECOSIMHLT --datatier RAWRECOSIM --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 --era Run2_2016 --step NONE --runUnscheduled --customise TauAnalysis/MCEmbeddingTools/customisers.customisoptions,TauAnalysis/MCEmbeddingTools/customisers.customiseFilterTTbartoMuMu --fileout PreRAWskimmed.root -n 100 --no_exec --python_filename=preselection.py
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('NONE',eras.Run2_2016)

# import of standard configurations
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/00244B75-3DA5-E611-9FC4-0CC47A4D76D0.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/003332DF-3CA5-E611-B27C-0CC47A4D764C.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/0059C5F0-35A5-E611-AE08-0CC47A74527A.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/00C6AD92-07A5-E611-B5FB-0CC47A4D76C8.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/00E2AA44-28A5-E611-8117-0025905A60B8.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/00FF5802-40A5-E611-977D-0CC47A78A42E.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/022027D6-A8A4-E611-8E64-001E674DA838.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/026FACAD-8DA5-E611-A5DD-0CC47A1DF80C.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/0274D239-2CA5-E611-B40E-0025905B860C.root', 
        '/store/mc/RunIISummer16DR80/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RAWAODSIM/FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/110000/02836714-C2A4-E611-951D-001E673E0206.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    allowUnscheduled = cms.untracked.bool(True)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('step0p5 nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RAWRECOSIMHLToutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('RAWRECOSIM'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    fileName = cms.untracked.string('PreRAWskimmed.root'),
    outputCommands = process.RAWRECOSIMHLTEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '80X_mcRun2_asymptotic_2016_TrancheIV_v6', '')

# Path and EndPath definitions
process.RAWRECOSIMHLToutput_step = cms.EndPath(process.RAWRECOSIMHLToutput)

# Schedule definition
process.schedule = cms.Schedule(process.RAWRECOSIMHLToutput_step)

# customisation of the process.

# Automatic addition of the customisation function from TauAnalysis.MCEmbeddingTools.customisers
from TauAnalysis.MCEmbeddingTools.customisers import customisoptions,customiseFilterTTbartoMuMu 

#call to customisation function customisoptions imported from TauAnalysis.MCEmbeddingTools.customisers
process = customisoptions(process)

#call to customisation function customiseFilterTTbartoMuMu imported from TauAnalysis.MCEmbeddingTools.customisers
process = customiseFilterTTbartoMuMu(process)

# End of customisation functions
#do not add changes to your config after this point (unless you know what you are doing)
from FWCore.ParameterSet.Utilities import convertToUnscheduled
process=convertToUnscheduled(process)
from FWCore.ParameterSet.Utilities import cleanUnscheduled
process=cleanUnscheduled(process)

