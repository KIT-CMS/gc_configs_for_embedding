#!/usr/bin/env python
import argparse
import os
import stat
import yaml
from scripts.EmbeddingTask import Preselection, FullTask
from scripts.filelist_generator import PreselectionFilelist, FullFilelist
import getpass


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Setup Grid Control for Embedding Production")
    parser.add_argument("--workdir",
                        type=str,
                        help="path to the workdir",
                        default="")
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
                        help="Name of the Run you want to process")
    parser.add_argument("--mode",
                        type=str,
                        required=True,
                        choices=['preselection', 'full'],
                        help="Select preselection mode of full embedding mode")
    parser.add_argument("--task",
                        type=str,
                        required=True,
                        choices=[
                            'setup_cmssw', 'upload_tarballs', 'setup_jobs',
                            'run_production', 'create_filelist',
                            'publish_dataset'
                        ],
                        help="Different commands that are possible")
    parser.add_argument(
        "--backend",
        type=str,
        choices=['etp', 'naf', 'cern'],
        help="Select the condor backend that is used -- TODO --")

    return parser.parse_args()


def possible_runs(era):
    config = yaml.load(open("scripts/ul_config.yaml", 'r'))
    runlist = config["runlist"][era]
    return runlist


class Task(object):
    def __init__(self, era, workdir, configdir, config, backend, run):
        self.era = era
        self.workdir = workdir
        self.config = config
        self.configdir = configdir
        self.runlist = self.validate_run(run)
        self.gc_path = os.path.abspath("grid-control")
        self.backend = backend
        self.cmssw_versions = {
            "main": self.config["cmssw_version"][self.era]["main"],
            "hlt": self.config["cmssw_version"][self.era]["hlt"]
        }
        self.username = getpass.getuser()

    def run_production(self):
        print("Running production for - {era} - {run}".format(
            era=self.era, run=self.runlist))
        configlist = []
        for run in self.runlist:
            configlist.append("{name}/{run}.conf".format(
                name=self.task.get_name(), run=run))
        out_file = open('{name}/while.sh'.format(name=self.task.get_name()),
                        'w')
        out_file.write('#!/bin/bash\n')
        out_file.write('\n')
        out_file.write('touch .lock\n')
        out_file.write('\n')
        out_file.write('while [ -f ".lock" ]\n')
        out_file.write('do\n')
        for config in configlist:
            out_file.write('{gc_path}/go.py {configpath} -G \n'.format(
                gc_path=self.gc_path, configpath=config))
        out_file.write('echo "rm .lock"\n')
        out_file.write('sleep 2\n')
        out_file.write('done\n')
        out_file.close()
        os.chmod('{name}/while.sh'.format(name=self.task.get_name()),
                 stat.S_IRWXU)
        os.system("./{name}/while.sh".format(name=self.task.get_name()))

    def setup_env(self):
        print("Setting up main CMSSW")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}.sh {VERSION}".format(
                ERA=self.era, VERSION=self.cmssw_versions["main"]))

        print("Setting up HLT CMSSW ")
        os.system(
            "bash scripts/UL_checkouts/checkout_UL_{ERA}_HLT.sh {VERSION}".
            format(ERA=self.era, VERSION=self.cmssw_versions["hlt"]))

    def validate_run(self, run):
        if run == "all":
            return self.config["runlist"][self.era]
        elif run in self.config["runlist"][self.era]:
            return [run]
        else:
            print("Run name unknown: Known runs are: {}".format(
                self.config["runlist"][self.era]))
            exit()

    @classmethod
    def build_filelist(self):
        pass

    @classmethod
    def publish_dataset(self):
        pass

    @classmethod
    def setup_cmsRun(self):
        pass

    @classmethod
    def upload_tarballs(self):
        pass


class PreselectionTask(Task):
    def __init__(self, era, workdir, configdir, config, backend, run):
        Task.__init__(self, era, workdir, configdir, config, backend, run)
        self.task = Preselection(era=self.era,
                                 workdir=self.workdir,
                                 identifier="data_{}".format(self.era),
                                 runs=self.runlist,
                                 inputfolder="Run2018_CMSSW_10_6_12_UL",
                                 config=self.config)

    def build_filelist(self):
        for run in self.runlist:
            filelist = PreselectionFilelist(configdir=self.configdir,
                                            era=self.era,
                                            grid_control_path=self.gc_path,
                                            run=run)
            filelist.build_filelist()

    def setup_cmsRun(self):
        self.task.setup_all()

    def upload_tarballs(self):
        print("Not needed for preselection --> Exiting ")

    def publish_dataset(self):
        print("Ne need to publish preselection datasets --> Exiting")


class EmbeddingTask(Task):
    def __init__(self, era, workdir, configdir, config, backend, run,
                 finalstate):
        Task.__init__(self, era, workdir, configdir, config, backend, run)
        self.finalstate = finalstate
        self.task = FullTask(finalstate=self.finalstate,
                             era=self.era,
                             workdir=self.workdir,
                             identifier="data_{}".format(self.era),
                             runs=self.runlist,
                             inputfolder="Run2018_CMSSW_10_6_12_UL",
                             config=self.config)

    def build_filelist(self):
        for run in self.runlist:
            filelist = FullFilelist(configdir=self.configdir,
                                    era=self.era,
                                    grid_control_path=self.gc_path,
                                    finalstate=self.finalstate,
                                    run=run)
            filelist.build_filelist()

    def publish_dataset(self):
        print("Implementation to be done")

    def setup_cmsRun(self):
        self.task.setup_all()

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
            cmd = "gfal-copy {outputfile} {tarballpath}/{TARBALLNAME}".format(
                outputfile=outputfile,
                tarballpath=config["output_paths"]["tarballs"].replace(
                    "{USER}", self.username),
                TARBALLNAME=outputfile)
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
                                args.backend, args.run)
    else:
        task = EmbeddingTask(args.era, args.workdir, configdir, config,
                             args.backend, args.run, args.final_state)
    if args.task == "setup_cmssw":
        task.setup_env()
    elif args.task == "upload_tarballs":
        task.upload_tarballs()
    elif args.task == "run_production":
        task.run_production()
    elif args.task == "create_filelist":
        task.build_filelist()
    elif args.task == "setup_jobs":
        task.setup_cmsRun()
    elif args.task == "publish_dataset":
        task.publish_dataset()
    else:
        exit()