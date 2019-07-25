from Prepare_all import finale_state

if __name__ == "__main__":
#	final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
	final_states=["ElTau"]
	dbs_map = {}
	dbs_map["DoubleMuon_C-v2"]="DoubleMuon/Run2016C-v2/RAW"
	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="data_2016_CMSSW8033", runs=["Run2016C"], inputfolder="Run2016_CMSSW_8_0_33", add_dbs=dbs_map, reselect=False)
