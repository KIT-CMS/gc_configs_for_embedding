import argparse
import subprocess
import os
import yaml
from scripts.Prepare_all_UL import FinalState
from scripts.filelist_generator import PreselectionFilelist, FullFilelist


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
                        choices=['preselection', 'all'],
                        help="Select preselection mode of full embedding mode")
    parser.add_argument("--task",
                        type=str,
                        required=True,
                        choices=[
                            'setup_cmssw', 'setup_jobs', 'create_filelist',
                            'publish_dataset'
                        ],
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


class Task(object):
    def __init__(self, era, workdir, configdir, config, backend):
        self.era = era
        self.workdir = workdir
        self.config = config
        self.configdir = configdir
        self.runlist = config["runlist"][era]
        self.gc_path = os.path.abspath("grid-control")
        self.backend = backend

    @classmethod
    def build_filelist(self):
        pass

    @classmethod
    def setup_cmsRun(self):
        pass

    def setup_env(self):
        cmssw = [
            self.config["cmssw_version"][self.era]["main"],
            self.config["cmssw_version"][self.era]["hlt"]
        ]

        print("Setting up main CMSSW")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}.sh {VERSION}".format(
                ERA=self.era, VERSION=cmssw[0]))
        build_tarball(cmssw[0], self.era, "main")

        print("Setting up HLT CMSSW ")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}_HLT.sh {VERSION}".
            format(ERA=self.era, VERSION=cmssw[1]))
        build_tarball(cmssw[1], self.era, "HLT")


class PreselectionTask(Task):
    def __init__(self, era, workdir, configdir, config, backend):
        Task.__init__(self, era, workdir, configdir, config, backend)

    def build_filelist(self):
        for run in self.runlist:
            filelist = PreselectionFilelist(configdir=self.configdir,
                                            era=self.era,
                                            grid_control_path=self.gc_path,
                                            run=run)
            filelist.build_filelist()

    def setup_cmsRun(self):
        dbs_map = {}
        for run in self.runlist:
            dbs_map["DoubleMuon_{}-v1".format(
                run)] = "/DoubleMuon/{}-v1/RAW".format(run)
        task_config = FinalState(finalstate="preselection",
                                 identifier="data_{}".format(self.era),
                                 runs=self.runlist,
                                 era=self.era,
                                 inputfolder="Run2018_CMSSW_10_6_12_UL",
                                 add_dbs=dbs_map,
                                 workdir=self.workdir,
                                 reselect=False,
                                 preselection=True,
                                 config=self.config)
        task_config.setup_all()


class EmbeddingTask(Task):
    def __init__(self, era, workdir, configdir, config, backend, finalstate):
        Task.__init__(self, era, workdir, configdir, config, backend)
        self.finalstate = finalstate

    def build_filelist(self):
        for run in self.runlist:
            filelist = FullFilelist(configdir=self.configdir,
                                    era=self.era,
                                    grid_control_path=self.gc_path,
                                    finalstate=self.finalstate,
                                    run=run)
            filelist.build_filelist()

    def setup_cmsRun(self):
        task_config = FinalState(finalstate=self.finalstate,
                                 identifier="data_{}".format(self.era),
                                 runs=self.runlist,
                                 era=self.era,
                                 workdir=self.workdir,
                                 inputfolder="Run2018_CMSSW_10_6_12_UL",
                                 add_dbs=None,
                                 reselect=False,
                                 config=self.config)
        task_config.setup_all()


def setup_gc(era, final_state, mode, backend, config):
    pass


def build_filelist(mode, era, config, workdir, finalstate):
    if mode == "preselection":
        for run in config["runlist"][era]:
            filelist = PreselectionFilelist(workdir=workdir,
                                            era=era,
                                            finalstate=finalstate,
                                            run=run)
            filelist.build_filelist()
            #print("Saving output in {}".format())
    else:
        #TODO
        pass


if __name__ == "__main__":
    args = parse_arguments()
    config = yaml.load(open("scripts/ul_config.yaml", 'r'))
    configdir = os.path.dirname(os.path.realpath(__file__))
    # first setup CMSSW enviorements
    if args.mode == "preselection":
        task = PreselectionTask(args.era, args.workdir, configdir, config,
                                args.backend)
    else:
        task = EmbeddingTask(args.era, args.workdir, configdir, config,
                             args.backend, args.finalstate)
    if args.task == "setup_cmssw":
        task.setup_env()
    elif args.task == "create_filelist":
        task.build_filelist()
    elif args.task == "setup_jobs":
        task.setup_cmsRun()
    # build the required config with the modified config files and generator cuts
    # generate the two tarballs
    # write the grid control config
    # write the while script