from Prepare_all import finale_state

if __name__ == "__main__":
	final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="data_2018_CMSSW1020_preselect", runs=["Run2018B","Run2018C","Run2018D"], inputfolder="Run2018_CMSSW_10_2_0", add_dbs=None, reselect=False)
