from Prepare_all import finale_state

if __name__ == "__main__":

    final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
    for finalstate in final_states:
        finale_state(finalstate=finalstate,
                     identifier="data_legacy_2016_CMSSW8033",
                     runs=[
                         "Run2016B-v2", "Run2016C-v2", "Run2016D-v2", "Run2016E-v2",
                         "Run2016F-v1", "Run2016G-v1", "Run2016H-v1"
                     ],
                     inputfolder="Run2016_CMSSW_8_0_33",
                     add_dbs=None,
                     reselect=True)
