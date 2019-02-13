from Prepare_all import finale_state

dbs_map = {}
dbs_map["DoubleMuon_Run2018A-v1"]="/DoubleMuon/Run2018A-v1/RAW "


if __name__ == "__main__":
	final_states=["Preselection"]
	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="data_2018_CMSSW1020", runs=["Run2018A","Run2018B","Run2018C","Run2018D"], inputfolder="Run2018_CMSSW_10_2_0", add_dbs=dbs_map, reselect=False)

	final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="data_2018_CMSSW1020", runs=["Run2018A","Run2018B","Run2018C","Run2018D"], inputfolder="Run2018_CMSSW_10_2_0", add_dbs=None, reselect=False)