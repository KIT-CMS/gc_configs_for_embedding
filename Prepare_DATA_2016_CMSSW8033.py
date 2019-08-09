from Prepare_all import finale_state

if __name__ == "__main__":

    final_states=["MuTau","ElTau","ElMu","TauTau","MuEmb","ElEmb"]
    for finalstate in final_states:
        finale_state(finalstate=finalstate,
                     identifier="data_legacy_2016_CMSSW8033",
                     runs=[
                         "Run2016B-v2", "Run2016C", "Run2016D", "Run2016E",
                         "Run2016F", "Run2016G", "Run2016H"
                     ],
                     inputfolder="Run2016_CMSSW_8_0_33",
                     add_dbs=None,
                     reselect=True)
