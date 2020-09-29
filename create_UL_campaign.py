import argparse
import subprocess
import os
import yaml
from scripts.Prepare_all_UL import FinalState
from scripts.filelist_generator import Filelist

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Setup Grid Control for Embedding Production")
    parser.add_argument("--workdir", type=str, help="path to the workdir")
    parser.add_argument(
        "--era",
        type=str,
        #choices=['2016_preVFP', '2016_postVFP', '2017', '2018'],
        choices=['2018'],
        required=True,
        help="Era used for the production")
    parser.add_argument(
        "--final-state",
        type=str,
        choices=["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"],
        help="Name the final state you want to process")
    parser.add_argument("--mode",
                        type=str,
                        required=True,
                        choices=['preselection', 'all', 'setup', 'filelist'],
                        help="Different commands that are possible")
    parser.add_argument("--backend",
                        type=str,
                        choices=['etp', 'naf', 'cern'],
                        help="Select the condor backend that is used")

    return parser.parse_args()


def build_tarball(cmssw_dir, era, type):
    print("building tarball...")
    outputfile = "cmssw_{ERA}_{TYPE}.tar.gz".format(ERA=era, TYPE=type)
    cmd = "tar --dereference -czf {FILE} {DIR}/*".format(
        FILE=outputfile,
        DIR=cmssw_dir,
    )
    print(cmd)
    os.system(cmd)
    print("finished tarball...")
    return (outputfile)


def setup_env(era, config):
    cmssw = [config["cmssw_version"][era]["main"], config["cmssw_version"][era]["hlt"]]
    print("Setting up main CMSSW : ")
    #rc = subprocess.call("scripts/UL_checkouts/checkout_UL_{ERA}.sh".format(ERA=era))
    os.system("bash scripts/UL_checkouts/checkout_UL_{ERA}.sh {VERSION}".format(ERA=era, VERSION=cmssw[0]))
    # all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    # latest_subdir = max(all_subdirs, key=os.path.getmtime)
    build_tarball(cmssw[0], era, "main")
    print("Setting up HLT CMSSW ")

    rc = subprocess.call("scripts/UL_checkouts/checkout_UL_{ERA}_HLT.sh {VERSION}".format(ERA=era, VERSION=cmssw[1]))
    # all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    # latest_subdir = max(all_subdirs, key=os.path.getmtime)
    build_tarball(cmssw[1], era, "HLT")


def setup_cmsRun(era, finalstate, mode, config, workdir):
    
    for run in config["runlist"][era]:
        dbs_map = {}
        dbs_map["DoubleMuon_{}-v1".format(
            run)] = "/DoubleMuon/{}-v1/RAW".format(run)
    if mode == "preselection":
        task_config = FinalState(finalstate=finalstate,
                        identifier="data_{}".format(era),
                        runs=config["runlist"][era],
                        era=era,
                        inputfolder="Run2018_CMSSW_10_6_12_UL",
                        add_dbs=dbs_map, workdir=workdir,
                        reselect=False, preselection=True, config=config)
        task_config.setup_all()
    elif mode == "all":
        task_config = FinalState(finalstate=finalstate,
                     identifier="data_{}".format(era),
                     runs=config["runlist"][era],
                     era=era, workdir=workdir,
                     inputfolder="Run2018_CMSSW_10_6_12_UL",
                     add_dbs=None,
                     reselect=False, config=config)
        task_config.setup_all()
    else:
        "Nothing to setup --> Ending"
    

def setup_gc(era, final_state, mode, backend, config):
    pass


if __name__ == "__main__":
    args = parse_arguments()
    config = yaml.load(open("scripts/ul_config.yaml", 'r'))
    # first setup CMSSW enviorements
    if args.mode == "setup":
        setup_env(args.era, config)
    elif args.mode == "filelist":
        build_filelist()
    else:
        setup_cmsRun(args.era, args.final_state, args.mode, config,args.workdir)
        setup_gc(args.era, args.final_state, args.mode, args.backend, config)
    # build the required config with the modified config files and generator cuts
    # generate the two tarballs
    # write the grid control config
    # write the while script