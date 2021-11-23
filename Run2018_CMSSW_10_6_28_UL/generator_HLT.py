# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py --filein file:simulated_and_cleaned_preHLT.root --fileout simulated_and_cleaned_posthlt.root --conditions 102X_upgrade2018_realistic_v15 --era Run2_2018 --eventcontent RAWSIM --step HLT:2018v32 --datatier RAWSIM --customise_commands process.source.bypassVersionCheck = cms.untracked.bool(True) --beamspot Realistic25ns13TeVEarly2018Collision --no_exec -n -1 --python_filename generator_HLT.py --geometry DB:Extended --mc
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

# In order to reduce diskusage of job, remove output of lheprodandcleaning.py --> lhe_and_cleaned.root
import os
if os.path.exists("lhe_and_cleaned.root"):
  os.remove("lhe_and_cleaned.root")

process = cms.Process('HLTEMB',eras.Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('HLTrigger.Configuration.HLT_2018v32_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:simulated_and_cleaned_preHLT.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('TauAnalysis/MCEmbeddingTools/python/EmbeddingPythia8Hadronizer_cfi.py nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('RAWSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('simulated_and_cleaned_posthlt.root'),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '102X_upgrade2018_realistic_v15', '')

# Path and EndPath definitions
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
process.schedule = cms.Schedule()
process.schedule.extend(process.HLTSchedule)
process.schedule.extend([process.endjob_step,process.RAWSIMoutput_step])
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from HLTrigger.Configuration.customizeHLTforMC
from HLTrigger.Configuration.customizeHLTforMC import customizeHLTforMC 

#call to customisation function customizeHLTforMC imported from HLTrigger.Configuration.customizeHLTforMC
process = customizeHLTforMC(process)

# End of customisation functions

# Customisation from command line
# Automatic addition of the customisation function from TauAnalysis.MCEmbeddingTools.customisers
from TauAnalysis.MCEmbeddingTools.customisers import customiseGenerator_HLT_Reselect

#call to customisation function customiseGenerator_Reselect imported from TauAnalysis.MCEmbeddingTools.customisers
process = customiseGenerator_HLT_Reselect(process)

process.source.bypassVersionCheck = cms.untracked.bool(True)
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
