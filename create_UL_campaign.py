import argparse
import subprocess
import os
import yaml
from scripts.EmbeddingTask import Preselection, FullTask
from scripts.filelist_generator import PreselectionFilelist, FullFilelist
import getpass


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
    parser.add_argument("--run",
                        type=str,
                        help="Name the final state you want to process")
    parser.add_argument("--mode",
                        type=str,
                        required=True,
                        choices=['preselection', 'full'],
                        help="Select preselection mode of full embedding mode")
    parser.add_argument("--task",
                        type=str,
                        required=True,
                        choices=[
                            'setup_cmssw', 'setup_jobs', 'upload_tarballs',
                            'create_filelist', 'publish_dataset'
                        ],
                        help="Different commands that are possible")
    parser.add_argument("--backend",
                        type=str,
                        choices=['etp', 'naf', 'cern'],
                        help="Select the condor backend that is used")

    return parser.parse_args()


def possible_runs(era):
    config = yaml.load(open("scripts/ul_config.yaml", 'r'))
    runlist = config["runlist"][era]
    return runlist


class Task(object):
    def __init__(self, era, workdir, configdir, config, backend):
        self.era = era
        self.workdir = workdir
        self.config = config
        self.configdir = configdir
        self.runlist = config["runlist"][era]
        self.gc_path = os.path.abspath("grid-control")
        self.backend = backend
        self.cmssw_versions = {
            "main": self.config["cmssw_version"][self.era]["main"],
            "hlt": self.config["cmssw_version"][self.era]["hlt"]
        }
        self.username = getpass.getuser()

    @classmethod
    def build_filelist(self):
        pass

    @classmethod
    def setup_cmsRun(self):
        pass

    @classmethod
    def upload_tarballs(self):
        pass

    def setup_env(self):
        print("Setting up main CMSSW")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}.sh {VERSION}".format(
                ERA=self.era, VERSION=self.cmssw_versions["main"]))

        print("Setting up HLT CMSSW ")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}_HLT.sh {VERSION}".
            format(ERA=self.era, VERSION=self.cmssw_versions["hlt"]))


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
        task = Preselection(era=self.era, workdir=self.workdir, identifier="data_{}".format(self.era), runs=self.runlist, inputfolder="Run2018_CMSSW_10_6_12_UL", config=self.config)
        task.setup_all()

    def upload_tarballs(self):
        print("Not needed for preselection --> Exiting ")


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
        task = FullTask(finalstate=self.finalstate,era=self.era, workdir=self.workdir, identifier="data_{}".format(self.era), runs=self.runlist, inputfolder="Run2018_CMSSW_10_6_12_UL",config=self.config)
        task.setup_all()

    def upload_tarballs(self):
        print("building tarball...")
        for version in self.cmssw_versions.values():
            outputfile = "cmssw_{VERSION}.tar.gz".format(VERSION=version)
            cmd = "tar --dereference -czf {FILE} {CMSSW_FOLDER}/*".format(
                FILE=outputfile,
                CMSSW_FOLDER=version,
            )
            print(cmd)
            os.system(cmd)
            print("finished building tarball...")
            print("upload tarball...")
            cmd = "gfal-copy {outputfile} {tarballpath}".format(
                outputfile=outputfile,
                tarballpath=config["output_paths"]["tarballs"].replace("{USER}",
                    self.username))
            print(cmd)
            os.system(cmd)
            print("finished uploading tarball...")


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
                             args.backend, args.final_state)
    if args.task == "setup_cmssw":
        task.setup_env()
    elif args.task == "upload_tarballs":
        task.upload_tarballs()
    elif args.task == "create_filelist":
        task.build_filelist()
    elif args.task == "setup_jobs":
        task.setup_cmsRun()
    # build the required config with the modified config files and generator cuts
    # generate the two tarballs
    # write the grid control config
    # write the while script