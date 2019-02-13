from Prepare_all import finale_state


if __name__ == "__main__":
	#final_states=["MuTau","ElTau","ElMu","TauTau"]
	final_states=["MuTau"]
	dbs_map = {}
	dbs_map["DYJetsToLLM50_FlatPU28to62"]="/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16DR80-FlatPU28to62HcalNZSRAWAODSIM_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/RAWAODSIM"

	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="MCttbar_2016_CMSSW826p1",runs=[], inputfolder="MC2016_CMSSW_8_0_26_p1", add_dbs=dbs_map)
