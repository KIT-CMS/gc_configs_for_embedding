# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: step0p5 --filein file:DYJetsToLL_2017.root --mc --eventcontent RAWRECOSIMHLT --datatier RAWRECOSIM --conditions 90X_upgrade2017_realistic_v20 --era Run2_2017 --step NONE --runUnscheduled --customise TauAnalysis/MCEmbeddingTools/customisers.customisoptions,TauAnalysis/MCEmbeddingTools/customisers.customiseFilterZToMuMu --fileout PreRAWskimmed.root -n 100 --no_exec --python_filename=preselection.py --geometry DB:Extended
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('NONE',eras.Run2_2017)

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
    fileNames = cms.untracked.vstring('file:DYJetsToLL_2017.root'),
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
process.GlobalTag = GlobalTag(process.GlobalTag, '90X_upgrade2017_realistic_v20', '')

# Path and EndPath definitions
process.RAWRECOSIMHLToutput_step = cms.EndPath(process.RAWRECOSIMHLToutput)

# Schedule definition
process.schedule = cms.Schedule(process.RAWRECOSIMHLToutput_step)

# customisation of the process.

# Automatic addition of the customisation function from TauAnalysis.MCEmbeddingTools.customisers
from TauAnalysis.MCEmbeddingTools.customisers import customisoptions,customiseFilterZToMuMu 

#call to customisation function customisoptions imported from TauAnalysis.MCEmbeddingTools.customisers
process = customisoptions(process)

#call to customisation function customiseFilterZToMuMu imported from TauAnalysis.MCEmbeddingTools.customisers
process = customiseFilterZToMuMu(process)

# End of customisation functions
#do not add changes to your config after this point (unless you know what you are doing)
from FWCore.ParameterSet.Utilities import convertToUnscheduled
process=convertToUnscheduled(process)
from FWCore.ParameterSet.Utilities import cleanUnscheduled
process=cleanUnscheduled(process)


# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
