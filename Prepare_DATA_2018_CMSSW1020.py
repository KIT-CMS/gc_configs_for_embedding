from Prepare_all import finale_state




if __name__ == "__main__":






	final_states=["MuTau"]
	for finalstate in final_states:
		finale_state(finalstate=finalstate, identifier="data_2018ABC_CMSSW1020", runs=["Run2018A","Run2018B","Run2018C"], inputfolder="Run2018ABC_CMSSW_10_2_0", add_dbs=None, reselect=False)
	exit()
	## Different globaltag for Run2018D

        final_states=["Preselection"]
        for run in ["Run2018D"]:
                dbs_map = {}
                dbs_map["DoubleMuon_{}-v1".format(run)]="/DoubleMuon/{}-v1/RAW".format(run)
                for finalstate in final_states:
                        finale_state(finalstate=finalstate, identifier="data_2018D_CMSSW1020", runs=[run], inputfolder="Run2018D_CMSSW_10_2_0", add_dbs=dbs_map, reselect=False)
        final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
        for finalstate in final_states:
                finale_state(finalstate=finalstate, identifier="data_2018D_CMSSW1020", runs=["Run2018D"], inputfolder="Run2018D_CMSSW_10_2_0", add_dbs=None, reselect=False)

