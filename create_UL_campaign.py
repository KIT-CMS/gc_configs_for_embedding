import argparse
import subprocess
import os
import yaml
from scripts.Prepare_all_UL import finale_state


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
        required=True,
        choices=["MuTau", "ElTau", "ElMu", "TauTau", "MuEmb", "ElEmb"],
        help="Name the final state you want to process")
    parser.add_argument("--mode",
                        type=str,
                        required=True,
                        choices=['preselection', 'full', 'setup'],
                        help="Setup preselection or full embedding chain")
    parser.add_argument("--backend",
                        type=str,
                        choices=['etp', 'naf', 'cern'],
                        help="Setup preselection or full embedding chain")

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


def setup_env(workdir, era):
    print("Setting up main CMSSW ")
    rc = subprocess.call("scripts/UL_checkouts/checkout_UL_{ERA}.sh ".format(ERA=era))
    all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    build_tarball(latest_subdir, era, "main")
    print("Setting up HLT CMSSW ")

    rc = subprocess.call("scripts/UL_checkouts/checkout_UL_{ERA}_HLT.sh ".format(ERA=era))
    all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    build_tarball(latest_subdir, era, "HLT")


def setup_cmsRun(era, finalstate, mode):
    configdict = yaml.load(open("ul_config", 'r'))
    for run in configdict["runlist"][era]:
        dbs_map = {}
        dbs_map["DoubleMuon_{}-v1".format(
            run)] = "/DoubleMuon/{}-v1/RAW".format(run)
        if mode == "preselection":
            finale_state(finalstate=finalstate,
                         identifier="data_{}_preselection".format(era),
                         runs=[run],
                         era=era,
                         inputfolder="Run2018_CMSSW_10_6_12_UL",
                         add_dbs=dbs_map,
                         reselect=False)
    if mode == "all":
        finale_state(finalstate=finalstate,
                     identifier="data_{}".format(era),
                     runs=configdict["runlist"][era],
                     era=era,
                     inputfolder="Run2018_CMSSW_10_6_12_UL",
                     add_dbs=None,
                     reselect=False)


def setup_gc(era, final_state, mode, backend):
    pass


if __name__ == "__main__":
    args = parse_arguments()
    # first setup CMSSW enviorements
    if args.mode == "setup":
        setup_env(args.era)
    else:
        setup_cmsRun(args.era, args.final_state, args.mode)
        setup_gc(args.era, args.final_state, args.mode, args.backend)
    # build the required config with the modified config files and generator cuts
    # generate the two tarballs
    # write the grid control config
    # write the while script
    main(args)