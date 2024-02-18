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

# add additional filters to TrigObj_filterBits column in NANOAOD
# these filters are needed in order to process the correct trigger object matching for applying
# the trigger scale factors on embedding samples

# modify the electron entry
process.triggerObjectTable.selections[0].qualityBits = cms.string(
    "filter('*CaloIdLTrackIdLIsoVL*TrackIso*Filter') + " \
    "2*filter('hltEle*WPTight*TrackIsoFilter*') + " \
    "4*filter('hltEle*WPLoose*TrackIsoFilter') + " \
    "8*filter('*OverlapFilter*IsoEle*PFTau*') + " \
    "16*filter('hltEle*Ele*CaloIdLTrackIdLIsoVL*Filter') + " \
    "32*filter('hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*')  + " \
    "64*filter('hlt*OverlapFilterIsoEle*PFTau*') + " \
    "128*filter('hltEle*Ele*Ele*CaloIdLTrackIdLDphiLeg*Filter') + " \
    "256*max(filter('hltL3fL1Mu*DoubleEG*Filtered*'),filter('hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter')) + " \
    "512*max(filter('hltL3fL1DoubleMu*EG*Filter*'),filter('hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter')) + " \
    "1024*min(filter('hltEle32L1DoubleEGWPTightGsfTrackIsoFilter'),filter('hltEGL1SingleEGOrFilter')) + " \
    "2048*filter('hltEle*CaloIdVTGsfTrkIdTGsfDphiFilter') + " \
    "4096*path('HLT_Ele*PFJet*') + " \
    "8192*max(filter('hltEG175HEFilter'),filter('hltEG200HEFilter')) + " \
    "16384*filter('hltEle27WPTightGsfTrackIsoFilter') + " \
    "32768*filter('hltEle32WPTightGsfTrackIsoFilter') + " \
    "65536*filter('hltEle35noerWPTightGsfTrackIsoFilter') + " \
    "131072*filter('hltEle32L1DoubleEGWPTightGsfTrackIsoFilter') + " \
    "262144*filter('hltEle24erWPTightGsfTrackIsoFilterForTau')" \
)

# add documentation for electron filter bits
process.triggerObjectTable.selections[0].qualityBitsDoc = cms.string(
    "1 = CaloIdL_TrackIdL_IsoVL, " \
    "2 = 1e (WPTight), " \
    "4 = 1e (WPLoose), " \
    "8 = OverlapFilter PFTau, " \
    "16 = 2e, " \
    "32 = 1e-1mu, " \
    "64 = 1e-1tau, " \
    "128 = 3e, " \
    "256 = 2e-1mu, " \
    "512 = 1e-2mu, " \
    "1024 = 1e (32_L1DoubleEG_AND_L1SingleEGOr), " \
    "2048 = 1e (CaloIdVT_GsfTrkIdT), " \
    "4096 = 1e (PFJet), " \
    "8192 = 1e (Photon175_OR_Photon200), " \
    "16384 = 1e (for e leg trigger object matching in embedding, path HLT_Ele27_WPTight_Gsf), " \
    "32768 = 1e (for e leg trigger object matching in embedding, path HLT_Ele32_WPTight_Gsf), " \
    "65536 = 1e (for e leg trigger object matching in embedding, path HLT_Ele35_WPTight_Gsf), " \
    "131072 = 1e (for e leg trigger object matching in embedding, path HLT_Ele32_WPTight_L1DoubleEG), " \
    "262144 = e-tau (for e leg trigger object matching in embedding, path HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau*30_eta2p1_CrossL1)"
)

# modify the muon entry
process.triggerObjectTable.selections[2].qualityBits = cms.string(
    "filter('*RelTrkIsoVVLFiltered0p4') + " \
    "2*filter('hltL3crIso*Filtered0p07') + " \
    "4*filter('*OverlapFilterIsoMu*PFTau*') + " \
    "8*max(filter('hltL3crIsoL1*SingleMu*Filtered0p07'),filter('hltL3crIsoL1sMu*Filtered0p07')) + " \
    "16*filter('hltDiMuon*Filtered*') + " \
    "32*filter('hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*') + " \
    "64*filter('hlt*OverlapFilterIsoMu*PFTau*') + " \
    "128*filter('hltL3fL1TripleMu*') + " \
    "256*max(filter('hltL3fL1DoubleMu*EG*Filtered*'),filter('hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter')) + " \
    "512*max(filter('hltL3fL1Mu*DoubleEG*Filtered*'),filter('hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter')) + " \
    "1024*max(filter('hltL3fL1sMu*L3Filtered50*'),filter('hltL3fL1sMu*TkFiltered50*')) + " \
    "2048*max(filter('hltL3fL1sMu*L3Filtered100*'),filter('hltL3fL1sMu*TkFiltered100*')) + " \
    "4096*filter('hltL3crIsoL1sSingleMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p07') + " \
    "8192*filter('hltL3crIsoL1sMu22Or25L1f0L2f10QL3f27QL3trkIsoFiltered0p07') + " \
    "16384*filter('hltL3crIsoL1sMu18erTau24erIorMu20erTau24erL1f0L2f10QL3f20QL3trkIsoFiltered0p07') + " \
    "32768*filter('hltL3crIsoBigORMu18erTauXXer2p1L1f0L2f10QL3f20QL3trkIsoFiltered0p07')"
)

# add documentation for muon filter bits
process.triggerObjectTable.selections[2].qualityBitsDoc = cms.string(
    "1 = TrkIsoVVL, " \
    "2 = Iso, " \
    "4 = OverlapFilter PFTau, " \
    "8 = 1mu, " \
    "16 = 2mu, " \
    "32 = 1mu-1e, " \
    "64 = 1mu-1tau, " \
    "128 = 3mu, " \
    "256 = 2mu-1e, " \
    "512 = 1mu-2e, " \
    "1024 = 1mu (Mu50), " \
    "2048 = 1mu (Mu100), " \
    "4096 = 1mu (for mu leg trigger object matching in embedding, path HLT_IsoMu24), " \
    "8192 = 1mu (for mu leg trigger object matching in embedding, path HLT_IsoMu27), " \
    "16384 = mu-tau (for mu leg trigger object matching in embedding, path HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1 2017), " \
    "32768 = mu-tau (for mu leg trigger object matching in embedding, path HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1 2018)"
)

# modify the selection string in the tau entry
process.triggerObjectTable.selections[3].sel = cms.string(
    "( type(84) || type(-100) ) && " \
    "(pt > 5) && " \
    "coll('*Tau*') &&" \
    "( filter('*LooseChargedIso*') || " \
    "filter('*MediumChargedIso*') || " \
    "filter('*DeepTau*') || " \
    "filter('*TightChargedIso*') || " \
    "filter('*TightOOSCPhotons*') || " \
    "filter('hltL2TauIsoFilter') || " \
    "filter('*OverlapFilterIsoMu*') || " \
    "filter('*OverlapFilterIsoEle*') || " \
    "filter('*L1HLTMatched*') || " \
    "filter('*Dz02*') || " \
    "filter('*DoublePFTau*') || " \
    "filter('*SinglePFTau*') || " \
    "filter('hlt*SelectedPFTau') || " \
    "filter('*DisplPFTau*') )"
)

# modify the tau entry
process.triggerObjectTable.selections[3].qualityBits = cms.string(
    "filter('*LooseChargedIso*') + " \
    "2*filter('*MediumChargedIso*') + " \
    "4*filter('*TightChargedIso*') + " \
    "8*filter('*TightOOSCPhotons*') + " \
    "16*filter('*Hps*') + " \
    "32*filter('hltSelectedPFTau*MediumChargedIsolationL1HLTMatched*') + " \
    "64*filter('hltDoublePFTau*TrackPt1*ChargedIsolation*Dz02Reg') + " \
    "128*filter('hltOverlapFilterIsoEle*PFTau*') + " \
    "256*filter('hltOverlapFilterIsoMu*PFTau*') + " \
    "512*filter('hltDoublePFTau*TrackPt1*ChargedIsolation*') + " \
    "1024*filter('hltL1sBigORLooseIsoEGXXerIsoTauYYerdRMin0p3') + " \
    "2048*filter('hltL1sMu18erTau24erIorMu20erTau24er') + "
    "4096*filter('hltL1sBigORMu18erTauXXer2p1') + " \
    "8192*filter('hltDoubleL2IsoTau26eta2p2')"
)

# add documentation for tau filter bits
process.triggerObjectTable.selections[3].qualityBitsDoc = cms.string(
    "1 = LooseChargedIso, " \
    "2 = MediumChargedIso, " \
    "4 = TightChargedIso, " \
    "8 = TightID OOSC photons, " \
    "16 = HPS, " \
    "32 = single-tau + tau+MET, " \
    "64 = di-tau, " \
    "128 = e-tau, " \
    "256 = mu-tau, " \
    "512 = VBF+di-tau, " \
    "1024 = e-tau (for tau leg trigger object matching in embedding, path HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1), " \
    "2048 = mu-tau (for tau leg trigger object matching in embedding, path HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1 2017), " \
    "4096 = mu-tau (for tau leg trigger object matching in embedding, path HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1 2018), " \
    "8192 = di-tau (for tau leg trigger object matching in embedding, paths HLT_Double*ChargedIsoPFTau*_Trk1*_eta2p1_Reg)"
)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
