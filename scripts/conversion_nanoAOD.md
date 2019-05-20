# Commands to generate configs for embedded conversion to NanoAOD

For all years:

```py
process.nanoAOD_step = cms.Path(process.genParticleSequence + process.nanoSequenceCommon + process.nanoSequenceOnlyFullSim + process.muonMC + process.electronMC + process.photonMC + process.tauMC + process.globalTablesMC + process.btagWeightTable + process.genWeightsTable + process.genParticleTables)

process.unpackedPatTrigger.triggerResults = cms.InputTag('TriggerResults::SIMembedding')

process.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_SIMembedding")  # Trigger information
process.NANOAODoutput.outputCommands.append("keep edmTriggerResults_*_*_MERGE")  # MET filter flags
```

## 2016

```sh
cmsDriver.py nanoProd_16 -s NANO \
--data --eventcontent NANOAOD --datatier NANOAOD \
--no_exec --conditions 102X_dataRun2_nanoAOD_2016_v1 \
--era Run2_2016,run2_miniAOD_80XLegacy \
--filein file:test_16.root \
--fileout file:test_nano_16.root
```

## 2017

```sh
cmsDriver.py nanoProd_17 -s NANO \
--data --eventcontent NANOAOD --datatier NANOAOD \
--no_exec --conditions 102X_dataRun2_v8 \
--era Run2_2017,run2_nanoAOD_94XMiniAODv1 \
--filein file:test_17.root \
--fileout file:test_nano_17.root
```

## 2018 ABC

```sh
cmsDriver.py nanoProd_18abc -s NANO \
--data --eventcontent NANOAOD --datatier NANOAOD \
--no_exec --conditions 102X_dataRun2_Sep2018ABC_v2 \
--era Run2_2018,run2_nanoAOD_102Xv1 \
--filein file:test_18abc.root \
--fileout file:test_nano_18abc.root
```

## 2018 D

```sh
cmsDriver.py nanoProd_18d -s NANO \
--data --eventcontent NANOAOD --datatier NANOAOD \
--no_exec --conditions 102X_dataRun2_Prompt_v13 \
--era Run2_2018,run2_nanoAOD_102Xv1 \
--filein file:test_18d.root \
--fileout file:test_nano_18d.root
```
