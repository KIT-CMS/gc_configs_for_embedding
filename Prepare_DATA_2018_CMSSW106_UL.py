from scripts.Prepare_all import finale_state

if __name__ == "__main__":
    final_states = ["Preselection"]
    for run in ["Run2018A", "Run2018B", "Run2018C", "Run2018D"]:
        dbs_map = {}
        dbs_map["DoubleMuon_{}-v1".format(
            run)] = "/DoubleMuon/{}-v1/RAW".format(run)
        for finalstate in final_states:
            finale_state(finalstate=finalstate,
                         identifier="data_2018_CMSSW106",
                         runs=[run],
                         inputfolder="Run2018_CMSSW_10_6_12_UL",
                         add_dbs=dbs_map,
                         reselect=False)
    final_states = ["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"]
    for finalstate in final_states:
        finale_state(finalstate=finalstate,
                     identifier="data_2018_CMSSW106",
                     runs=["Run2018A", "Run2018B", "Run2018C", "Run2018D"],
                     inputfolder="Run2018_CMSSW_10_6_12_UL",
                     add_dbs=None,
                     reselect=False)
