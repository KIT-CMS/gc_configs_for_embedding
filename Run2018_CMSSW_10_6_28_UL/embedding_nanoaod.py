# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: -s NANO --data --eventcontent NANOAOD --datatier NANOAOD --no_exec --conditions 106X_dataRun2_v28 --era Run2_2018 --filein file:test_18.root --fileout file:test_nano_18.root --python_filename=embedding_nanoAOD.py
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018

process = cms.Process('NANO',Run2_2018)

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
    fileNames = cms.untracked.vstring('file:test_18.root'),
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

from TauAnalysis.MCEmbeddingTools.customisers import customiseNanoAOD
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
# add modifications from https://github.com/cms-sw/cmssw/pull/38472 to correctly handle trigger flags in NanoAOD
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
                            "8192*max(filter('hltEG175HEFilter'),filter('hltEG200HEFilter'))")

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
                            "2048*max(filter('hltL3fL1sMu*L3Filtered100*'),filter('hltL3fL1sMu*TkFiltered100*'))")
process.triggerObjectTable.selections[3] = cms.PSet(
            name = cms.string("Tau"),
            id = cms.int32(15),
            sel = cms.string("type(84) && pt > 5 && coll('*Tau*') && ( filter('*LooseChargedIso*') || filter('*MediumChargedIso*') || filter('*DeepTau*') || filter('*TightChargedIso*') || filter('*TightOOSCPhotons*') || filter('hltL2TauIsoFilter') || filter('*OverlapFilterIsoMu*') || filter('*OverlapFilterIsoEle*') || filter('*L1HLTMatched*') || filter('*Dz02*') || filter('*DoublePFTau*') || filter('*SinglePFTau*') || filter('hlt*SelectedPFTau') || filter('*DisplPFTau*') )"), #All trigger objects from a Tau collection + passing at least one filter
            l1seed = cms.string("type(-100)"), l1deltaR = cms.double(0.3),
            l2seed = cms.string("type(84) && coll('hltL2TauJetsL1IsoTauSeeded')"),  l2deltaR = cms.double(0.3),
            skipObjectsNotPassingQualityBits = cms.bool(True),
            qualityBits = cms.string(
                            "filter('*LooseChargedIso*') + " \
                            "2*filter('*MediumChargedIso*') + " \
                            "4*filter('*TightChargedIso*') + " \
                            "8*filter('*DeepTau*') + " \
                            "16*filter('*TightOOSCPhotons*') + " \
                            "32*filter('*Hps*') + " \
                            "64*filter('hlt*DoublePFTau*TrackPt1*ChargedIsolation*Dz02*') + " \
                            "128*filter('hlt*DoublePFTau*DeepTau*L1HLTMatched') + " \
                            "256*filter('hlt*OverlapFilterIsoEle*WPTightGsf*PFTau') + " \
                            "512*filter('hlt*OverlapFilterIsoMu*PFTau*') + " \
                            "1024*filter('hlt*SelectedPFTau*L1HLTMatched') + " \
                            "2048*filter('hlt*DoublePFTau*TrackPt1*ChargedIso*') + " \
                            "4096*filter('hlt*DoublePFTau*Track*ChargedIso*AgainstMuon') + " \
                            "8192*filter('hltHpsSinglePFTau*HLTMatched') + " \
                            "16384*filter('hltHpsOverlapFilterDeepTauDoublePFTau*PFJet*') + " \
                            "32768*filter('hlt*Double*ChargedIsoDisplPFTau*Dxy*') + " \
                            "65536*filter('*Monitoring') + " \
                            "131072*filter('*Reg') + " \
                            "262144*filter('*L1Seeded') + " \
                            "524288*filter('*1Prong')"),
            qualityBitsDoc = cms.string("1 = LooseChargedIso, 2 = MediumChargedIso, 4 = TightChargedIso, 8 = DeepTau, 16 = TightID OOSC photons, 32 = HPS, 64 = charged iso di-tau, 128 = deeptau di-tau, 256 = e-tau, 512 = mu-tau, 1024 = single-tau/tau+MET, 2048 = run 2 VBF+ditau, 4096 = run 3 VBF+ditau, 8192 = run 3 double PF jets + ditau, 16384 = di-tau + PFJet, 32768 = Displaced Tau, 65536 = Monitoring, 131072 = regional paths, 262144 = L1 seeded paths, 524288 = 1 prong tau paths"),
        )
process.triggerObjectTable.selections[4].qualityBits = cms.string(
                "1         * filter('*CrossCleaned*LooseChargedIsoPFTau*') + " \
                "2         * filter('hltBTagCaloCSVp087Triple') + " \
                "4         * filter('hltDoubleCentralJet90') + " \
                "8         * filter('hltDoublePFCentralJetLooseID90') + " \
                "16        * filter('hltL1sTripleJetVBFIorHTTIorDoubleJetCIorSingleJet') + " \
                "32        * filter('hltQuadCentralJet30') + " \
                "64        * filter('hltQuadPFCentralJetLooseID30') + " \
                "128       * max(filter('hltL1sQuadJetC50IorQuadJetC60IorHTT280IorHTT300IorHTT320IorTripleJet846848VBFIorTripleJet887256VBFIorTripleJet927664VBF'), filter('hltL1sQuadJetCIorTripleJetVBFIorHTT')) + " \
                "256       * filter('hltQuadCentralJet45') + " \
                "512       * filter('hltQuadPFCentralJetLooseID45') + " \
                "1024      * max(filter('hltL1sQuadJetC60IorHTT380IorHTT280QuadJetIorHTT300QuadJet'), filter('hltL1sQuadJetC50to60IorHTT280to500IorHTT250to340QuadJet')) + " \
                "2048      * max(filter('hltBTagCaloCSVp05Double'), filter('hltBTagCaloDeepCSVp17Double')) + " \
                "4096      * filter('hltPFCentralJetLooseIDQuad30') + " \
                "8192      * filter('hlt1PFCentralJetLooseID75') + " \
                "16384     * filter('hlt2PFCentralJetLooseID60') + " \
                "32768     * filter('hlt3PFCentralJetLooseID45') + " \
                "65536     * filter('hlt4PFCentralJetLooseID40') + " \
                "131072    * max(filter('hltBTagPFCSVp070Triple'), max(filter('hltBTagPFDeepCSVp24Triple'), filter('hltBTagPFDeepCSV4p5Triple')) )+ " \
                "262144    * filter('hltHpsOverlapFilterDeepTauDoublePFTau*PFJet*') + " \
                "524288   * filter('*CrossCleaned*MediumDeepTauDitauWPPFTau*') + " \
                "1048576   * filter('*CrossCleanedUsingDiJetCorrChecker*')"
                )
process.triggerObjectTable.selections[4].qualityBitsDoc = cms.string(
                "Jet bits: bit 0 for VBF cross-cleaned from loose iso PFTau, bit 1 for hltBTagCaloCSVp087Triple, bit 2 for hltDoubleCentralJet90, bit 3 for hltDoublePFCentralJetLooseID90," \
                " bit 4 for hltL1sTripleJetVBFIorHTTIorDoubleJetCIorSingleJet, bit 5 for hltQuadCentralJet30, bit 6 for hltQuadPFCentralJetLooseID30," \
                " bit 7 for hltL1sQuadJetC50IorQuadJetC60IorHTT280IorHTT300IorHTT320IorTripleJet846848VBFIorTripleJet887256VBFIorTripleJet927664VBF or hltL1sQuadJetCIorTripleJetVBFIorHTT," \
                " bit 8 for hltQuadCentralJet45, bit 9 for hltQuadPFCentralJetLooseID45," \
                " bit 10  for hltL1sQuadJetC60IorHTT380IorHTT280QuadJetIorHTT300QuadJet or hltL1sQuadJetC50to60IorHTT280to500IorHTT250to340QuadJet" \
                " bit 11 for hltBTagCaloCSVp05Double or hltBTagCaloDeepCSVp17Double, bit 12 for hltPFCentralJetLooseIDQuad30, bit 13 for hlt1PFCentralJetLooseID75," \
                " bit 14 for hlt2PFCentralJetLooseID60, bit 15 for hlt3PFCentralJetLooseID45, bit 16 for hlt4PFCentralJetLooseID40," \
                " bit 17 for hltBTagPFCSVp070Triple or hltBTagPFDeepCSVp24Triple or hltBTagPFDeepCSV4p5Triple,"\
                " bit 18 for Double tau + jet,"\
                " bit 19 for VBF cross-cleaned from medium deeptau PFTau,"+
                " bit 20 for VBF cross-cleaned using dijet correlation checker ")
process.triggerObjectTable.selections.append(
            cms.PSet(
            name = cms.string("BoostedTau"),
            id = cms.int32(1515),
            sel = cms.string("type(85) && pt > 120 && coll('hltAK8PFJetsCorrected') && filter('hltAK8SinglePFJets*SoftDropMass40*ParticleNetTauTau')"),
            l1seed = cms.string("type(-99)"), l1deltaR = cms.double(0.3),
            l2seed = cms.string("type(85)  && coll('hltAK8CaloJetsCorrectedIDPassed')"),  l2deltaR = cms.double(0.3),
            skipObjectsNotPassingQualityBits = cms.bool(True),
            qualityBits = cms.string(
                "filter('hltAK8SinglePFJets*SoftDropMass40*ParticleNetTauTau')"
                ),
            qualityBitsDoc = cms.string("Bit 0 for HLT_AK8PFJetX_SoftDropMass40_PFAK8ParticleNetTauTau0p30")))
# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
