from Prepare_all import finale_state

if __name__ == "__main__":
	final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]

	dbs_map = {}
	dbs_map["DYJetsToLLM50_NZSPU40to70"]="/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIWinter17DR-NZSPU40to70_94X_upgrade2018_realistic_v8-v3/GEN-SIM-RAW"

	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="MC_2017_CMSSW944", runs=[], inputfolder="MC2017_CMSSW_9_4_4", add_dbs=dbs_map)
