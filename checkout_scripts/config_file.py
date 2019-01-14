import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
      '/store/user/jbechtel/MuTau_data_2016_CMSSW826_freiburg/TauEmbedding_MuTau_data_2016_CMSSW826_Run2016B/1/merged_0.root'
   )
)
    
process.demo = cms.EDAnalyzer('GeneratorWeight',
               genSource = cms.InputTag("generator")
)

process.p = cms.Path(process.demo)
