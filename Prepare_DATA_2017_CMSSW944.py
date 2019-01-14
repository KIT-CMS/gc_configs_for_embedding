from Prepare_all import finale_state

if __name__ == "__main__":
	final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="data_2017_CMSSW944", runs=["Run2017B","Run2017C","Run2017D","Run2017E","Run2017F"], inputfolder="Run2017_CMSSW_9_4_4", add_dbs=None, reselect=True)
