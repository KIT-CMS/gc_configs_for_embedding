from Prepare_all import finale_state

if __name__ == "__main__":
	final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]

	dbs_map = {}
	dbs_map["DYJetsToLLM50_FlatPU28to62"]="/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/PhaseISpring17DR-FlatPU28to62HcalNZS_90X_upgrade2017_realistic_v20-v1/GEN-SIM-RAW"

	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="MC_2017_CMSSW902", runs=[], inputfolder="MC2017_CMSSW_9_0_2", add_dbs=dbs_map)
