#!/bin/sh

echo "bl"

##########datasetDBS3Add.py -F /portal/ekpbms1/home/wayand/embedding/gc_workdir/TauEmbedding_MuTau_test2_Run2016B/dbs/dbs.dat Run2016B.conf  -o -i 

datasetDBS3Add.py -n EmbeddingRun2016C/MuTauFinalState-imputDoubleMu_mirror_miniAOD-v5/USER Run2016C.conf -o
datasetDBS3Add.py -n EmbeddingRun2016B/MuTauFinalState-imputDoubleMu_mirror_miniAOD-v5/USER Run2016B.conf -o 
datasetDBS3Add.py -n EmbeddingRun2016D/MuTauFinalState-imputDoubleMu_mirror_miniAOD-v5/USER Run2016D.conf -o
datasetDBS3Add.py -n EmbeddingRun2016E/MuTauFinalState-imputDoubleMu_mirror_miniAOD-v5/USER Run2016E.conf -o
datasetDBS3Add.py -n EmbeddingRun2016F/MuTauFinalState-imputDoubleMu_mirror_miniAOD-v5/USER Run2016F.conf -o
datasetDBS3Add.py -n EmbeddingRun2016G/MuTauFinalState-imputDoubleMu_mirror_miniAOD-v5/USER Run2016G.conf -o
