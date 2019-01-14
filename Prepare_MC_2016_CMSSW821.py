from Prepare_all import finale_state


if __name__ == "__main__":
	#final_states=["MuTau","ElTau","ElMu","TauTau"]
	final_states=["TauTau","ElMu"]
	dbs_map = {}
	dbs_map["DYJetsToLLM50_FlatPU28to62"]="/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16DR80-FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v2/RAWAODSIM"

	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="MC_2016_CMSSW821",runs=[], inputfolder="MC2016_CMSSW_8_0_21", add_dbs=dbs_map)
